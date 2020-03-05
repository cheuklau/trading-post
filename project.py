# Import flask dependencies
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response

# Import SQLAlchemy dependencies
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

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
    if result['status'] == '200':
        # Delete login session
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        output += '<h1> Successfully disconnected </h1>'
    else:
        output += '<h1> Unable to disconnect user </h1>'
    # Button IP address should be a latebind
    output += """<a href = "http://0.0.0.0.xip.io:5000/">"""
    output += '<button class="btn-default">'
    output += '<span class="glyphicon" aria-hidden="true"></span>'
    output += 'Back to Catalog App </button> </a>'
    return output


@app.route('/category/JSON')
def categoryJSON():
    """ API endpoint to return all category names.

    """

    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/category/<int:category_id>/JSON')
def categoryItemsJSON(category_id):
    """ API endpoint to return all items of a given category.

    """

    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/items/JSON')
def itemsJSON():
    """ API endpoint to return all items.

    """

    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    """ Show items for selected category


    """

    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    if 'username' not in login_session:
        return render_template('publicitems.html',
                               categories=categories,
                               category=category,
                               items=items)
    else:
        return render_template('privateitems.html',
                               categories=categories,
                               category=category,
                               items=items)


@app.route('/items/<int:item_id>')
def showItem(item_id):
    """ Show individual item description


    """

    categories = session.query(Category).order_by(asc(Category.name))
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return render_template('publicitem.html',
                               categories=categories,
                               item=item)
    else:
        return render_template('privateitem.html',
                               categories=categories,
                               item=item)


@app.route('/additem', methods=['GET', 'POST'])
def addItem():
    """ Add item to database.

    """

    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')

    # If this is a post request from newitem.html
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category_id'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Item successfully added')
        return redirect(url_for('showMain'))
    else:
        return render_template('newitem.html')


@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    """ Edit selected item

    """

    editedItem = session.query(Item).filter_by(id=item_id).one()
    user = session.query(User).filter_by(email=login_session['email']).one()
    if request.method == 'POST':
        if user.id == editedItem.user_id:
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['category_id']:
                editedItem.category_id = request.form['category_id']
            session.add(editedItem)
            session.commit()
            flash('Item successfully edited')
            return redirect(url_for('showMain'))
        else:
            flash('User not authorized to edit item')
            return redirect(url_for('showMain'))
    else:
        if user.id == editedItem.user_id:
            return render_template('edititem.html', item=editedItem)
        else:
            flash('User not authorized to edit item')
            return redirect(url_for('showMain'))


@app.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    """ Delete selected item

    """

    deletedItem = session.query(Item).filter_by(id=item_id).one()
    user = session.query(User).filter_by(email=login_session['email']).one()
    if request.method == 'POST':
        if user.id == deletedItem.user_id:
            session.delete(deletedItem)
            session.commit()
            flash('Item successfully deleted')
            return redirect(url_for('showMain'))
        else:
            flash('User not authorized to delete item')
            return redirect(url_for('showMain'))
    else:
        if user.id == deletedItem.user_id:
            return render_template('deleteitem.html', item=deletedItem)
        else:
            flash('User not authorized to delete item')
            return redirect(url_for('showMain'))


@app.route('/')
def showMain():
    """ Main page showing the latest items.

    """

    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.time_added)).limit(5)
    if 'username' not in login_session:
        return render_template('publicmain.html',
                               categories=categories,
                               items=items)
    else:
        return render_template('privatemain.html',
                               categories=categories,
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
