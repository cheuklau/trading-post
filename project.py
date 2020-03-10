# Import flask dependencies
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response

# Import SQLAlchemy dependencies
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Location, Item, Message

# Imports for anti-forgery state token
from flask import session as login_session
import random, string, httplib2, json, requests

# Imports for GConnect
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# Create instance of flask class with the name of the running application
app = Flask(__name__)

# Create session and connect to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    """ Displays log-in page.

        Creates and passes anti-forgery state token to login page.
    """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Connects user to Google for third-party authorization.

    """

    # Confirm token client sent to server matches token from server
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token in session for later use
    access_token =  request.data
    login_session['access_token'] = access_token
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # See if user exists, if not then make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Create personalized response
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """ Disconnect user from Google.

    """

    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Revoke access token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=' + access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    output = ''
    # Delete login session
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    if result['status'] == '200':
        output += '<h1> Successfully disconnected </h1>'
    else:
        output += '<h1> Unable to disconnect user </h1>'
    # Button IP address should be a latebind
    output += """<a href = "http://0.0.0.0.xip.io:5000/">"""
    output += '<button class="btn-default">'
    output += '<span class="glyphicon" aria-hidden="true"></span>'
    output += 'Back to Catalog App </button> </a>'
    return output


@app.route('/location/JSON')
def locationJSON():
    """ API endpoint to return all location names.

    """

    locations = session.query(location).all()
    return jsonify(locations=[c.serialize for c in locations])


@app.route('/location/<int:location_id>/JSON')
def locationItemsJSON(location_id):
    """ API endpoint to return all items of a given location.

    """

    items = session.query(Item).filter_by(location_id=location_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/items/JSON')
def itemsJSON():
    """ API endpoint to return all items.

    """

    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/location/<int:location_id>/')
@app.route('/location/<int:location_id>/items/')
def showItems(location_id):
    """ Show items for selected location


    """

    locations = session.query(Location).order_by(asc(Location.name))
    location = session.query(Location).filter_by(id=location_id).one()
    items = session.query(Item).join(User).filter(User.location_id==location_id).all()
    if 'username' not in login_session:
        return render_template('publicitems.html',
                               locations=locations,
                               location=location,
                               items=items)
    else:
        # Update location of user
        user = session.query(User).filter_by(id=login_session['user_id']).one()
        user.location_id = location_id
        location = session.query(Location).filter_by(id=location_id).one()
        return render_template('privateitems.html',
                               user_id=login_session['user_id'],
                               locations=locations,
                               location=location,
                               items=items)


@app.route('/items/<int:item_id>', methods=['GET', 'POST'])
def showItem(item_id):
    """ Show individual item description


    """

    locations = session.query(Location).order_by(asc(Location.name))
    item = session.query(Item).filter_by(id=item_id).one()
    user = session.query(User).filter_by(id=login_session["user_id"]).one()
    if request.method == "POST":
        newMessage = Message(sender_id=login_session["user_id"],
                             receiver_id=item.user_id,
                             item_id=item_id,
                             message=request.form["message"])
        session.add(newMessage)
        session.commit()
        flash("Message sent")
        return redirect(url_for("showItems", location_id=user.location_id))
    else:
        return render_template('privateitem.html',
                                user_id=login_session['user_id'],
                                locations=locations,
                                item=item)


@app.route('/user/items/')
def showUserItems():
    """ Show items for user


    """

    locations = session.query(Location).order_by(asc(Location.name))
    items = session.query(Item).filter_by(user_id=login_session['user_id']).all()
    return render_template('useritems.html',
                            locations=locations,
                            items=items)


@app.route('/user/items/<int:item_id>')
def showUserItem(item_id):
    """ Show description for individual item belonging to user


    """

    locations = session.query(Location).order_by(asc(Location.name))
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('useritem.html',
                            user_id=login_session['user_id'],
                            locations=locations,
                            item=item)


@app.route('/user/messages')
def showUserMessages():
    """ Show user messages


    """

    locations = session.query(Location).order_by(asc(Location.name))
    messages = session.query(Message).filter_by(receiver_id=login_session["user_id"]).all()
    return render_template('usermessages.html',
                            user_id=login_session['user_id'],
                            messages=messages,
                            locations=locations)


@app.route('/messages/<int:message_id>/reply', methods=['GET', 'POST'])
def replyMessage(message_id):
    """ Reply to a message

    """

    locations = session.query(Location).order_by(asc(Location.name))
    message = session.query(Message).filter_by(id=message_id).one()
    user = session.query(User).filter_by(id=login_session['user_id']).one()
    item = session.query(Item).filter_by(id=message.item_id).one()
    if request.method == "POST":
        if user.id == replyMessage.receiver_id:
            newMessage = Message(sender_id=login_session["user_id"],
                                 receiver_id=replyMessage.sender_id,
                                 item_id=replyMessage.item_id,
                                 message=request.form["message"])
            session.add(newMessage)
            session.commit()
            flash("Reply sent")
            return redirect(url_for("showUserMessages"))
        else:
            flash("User not authorized")
            return redirect(url_for("showUserMessages"))
    else:
        return render_template("replymessage.html",
                               locations=locations,
                               message=message,
                               item=item)


@app.route('/items/<int:message_id>/delete', methods=['GET', 'POST'])
def deleteMessage(message_id):
    """ Delete selected message

    """

    locations = session.query(Location).order_by(asc(Location.name))
    message = session.query(Message).filter_by(id=message_id).one()
    user = session.query(User).filter_by(id=login_session['user_id']).one()
    if request.method == 'POST':
        if user.id == message.receiver_id:
            session.delete(message)
            session.commit()
            flash('Message deleted')
            return redirect(url_for('showUserMessages'))
        else:
            flash('User not authorized')
            return redirect(url_for('showUserMessages'))
    else:
        return render_template('deletemessage.html',
                               locations=locations,
                               message=message)


@app.route('/additem', methods=['GET', 'POST'])
def addItem():
    """ Add item to database.

    """

    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       cardset=request.form['cardset'],
                       condition=request.form['condition'],
                       price=request.form['price'],
                       quantity=request.form['quantity'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item added')
        return redirect(url_for('showUserItems'))
    else:
        return render_template('newitem.html')


@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    """ Edit selected item

    """

    locations = session.query(Location).order_by(asc(Location.name))
    editedItem = session.query(Item).filter_by(id=item_id).one()
    user = session.query(User).filter_by(id=login_session['user_id']).one()
    if request.method == "POST":
        if user.id == editedItem.user_id:
            editedItem.name = request.form["name"]
            editedItem.cardset = request.form["cardset"]
            editedItem.condition = request.form["condition"]
            editedItem.quantity = request.form["quantity"]
            editedItem.price = request.form["price"]
            session.add(editedItem)
            session.commit()
            flash("Item changed")
            return redirect(url_for("showUserItems"))
        else:
            flash("User not authorized")
            return redirect(url_for("showUserItems"))
    else:
        return render_template("edititem.html",
                               locations=locations,
                               item=editedItem)


@app.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    """ Delete selected item

    """

    locations = session.query(Location).order_by(asc(Location.name))
    deletedItem = session.query(Item).filter_by(id=item_id).one()
    user = session.query(User).filter_by(id=login_session['user_id']).one()
    if request.method == 'POST':
        if user.id == deletedItem.user_id:
            session.delete(deletedItem)
            session.commit()
            flash('Item deleted')
            return redirect(url_for('showUserItems'))
        else:
            flash('User not authorized')
            return redirect(url_for('showUserItems'))
    else:
        return render_template('deleteitem.html',
                               locations=locations,
                               item=deletedItem)


@app.route('/')
def showMain():
    """ Main page showing the latest items.

    """

    locations = session.query(Location).order_by(asc(Location.name))
    items = session.query(Item).order_by(desc(Item.time_added)).limit(5)
    if 'username' not in login_session:
        return render_template('publicmain.html',
                               locations=locations,
                               items=items)
    else:
        return render_template('privatemain.html',
                               locations=locations,
                               items=items)


def createUser(login_session):
    """ Helper function to set up user log-in.

        Add user to database, return user id.
    """

    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ Helper function to set up user login.

        Return user information given user id.
    """

    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """ Helper function to set up user login.

        Return user id given email.
    """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0.xip.io', port=5000)
