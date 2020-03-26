"""
Main trading post Flask application file
"""

import random
import string
import json
from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash, make_response, session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
import httplib2
import requests
from database_setup import BASE, User, Location, Item, Message

# Create instance of flask class with the name of the running application
APP = Flask(__name__)

# Create session and connect to database
ENGINE = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = ENGINE
DBSESSION = sessionmaker(bind=ENGINE)
SESSION = DBSESSION()

@APP.route('/login')
def show_login():
    """ Displays log-in page.

        Creates and passes anti-forgery state token to login page.
    """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@APP.route('/gconnect', methods=['POST'])
def gconnect():
    """ Connects user to Google for third-party authorization.

    """

    # Confirm token client sent to server matches token from server
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token in session for later use
    access_token = request.data
    login_session['access_token'] = access_token
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['email'] = data['email']
    # See if user exists, if not then make a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user()
    login_session['user_id'] = user_id
    # Create personalized response
    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['email'])
    return output


@APP.route('/gdisconnect')
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
    http_var = httplib2.Http()
    result = http_var.request(url, 'GET')[0]
    output = ''
    # Delete login session
    del login_session['access_token']
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


@APP.route('/<int:location>/JSON')
def location_json(location):
    """ API endpoint to return all location names.

    """

    locations = SESSION.query(location).all()
    return jsonify(locations=[c.serialize for c in locations])


@APP.route('/location/<int:location_id>/JSON')
def location_items_json(location_id):
    """ API endpoint to return all items of a given location.

    """

    items = SESSION.query(Item).filter_by(location_id=location_id).all()
    return jsonify(items=[i.serialize for i in items])


@APP.route('/items/JSON')
def items_json():
    """ API endpoint to return all items.

    """

    items = SESSION.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


@APP.route('/location/<int:location_id>/')
@APP.route('/location/<int:location_id>/items/')
def show_items(location_id):
    """ Show items for selected location


    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    location = SESSION.query(Location).filter_by(id=location_id).one()
    items = SESSION.query(Item).join(User).filter(User.location_id == location_id).all()
    if 'email' not in login_session:
        return render_template('publicitems.html',
                               locations=locations,
                               location=location,
                               items=items)
    # Update location of user
    user = SESSION.query(User).filter_by(id=login_session['user_id']).one()
    user.location_id = location_id
    location = SESSION.query(Location).filter_by(id=location_id).one()
    return render_template('privateitems.html',
                           user_id=login_session['user_id'],
                           locations=locations,
                           location=location,
                           items=items)


@APP.route('/items/<int:item_id>', methods=['GET', 'POST'])
def show_item(item_id):
    """ Show individual item description


    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    item = SESSION.query(Item).filter_by(id=item_id).one()
    user = SESSION.query(User).filter_by(id=login_session["user_id"]).one()
    if request.method == "POST":
        new_message = Message(sender_id=login_session["user_id"],
                              receiver_id=item.user_id,
                              item_id=item_id,
                              message=request.form["message"])
        SESSION.add(new_message)
        SESSION.commit()
        flash("Message sent")
        return redirect(url_for("show_items", location_id=user.location_id))
    return render_template('privateitem.html',
                           user_id=login_session['user_id'],
                           locations=locations,
                           item=item)


@APP.route('/user/items/')
def show_user_items():
    """ Show items for user


    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    items = SESSION.query(Item).filter_by(user_id=login_session['user_id']).all()
    return render_template('useritems.html',
                           locations=locations,
                           items=items)


@APP.route('/user/items/<int:item_id>')
def show_user_item(item_id):
    """ Show description for individual item belonging to user


    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    item = SESSION.query(Item).filter_by(id=item_id).one()
    return render_template('useritem.html',
                           user_id=login_session['user_id'],
                           locations=locations,
                           item=item)


@APP.route('/user/messages')
def show_user_messages():
    """ Show user messages


    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    messages = SESSION.query(Message) \
               .filter_by(receiver_id=login_session["user_id"]) \
               .join(Item) \
               .all()
    return render_template('usermessages.html',
                           user_id=login_session['user_id'],
                           messages=messages,
                           locations=locations)


@APP.route('/messages/<int:message_id>/reply', methods=['GET', 'POST'])
def reply_message(message_id):
    """ Reply to a message

    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    message = SESSION.query(Message).filter_by(id=message_id).one()
    user = SESSION.query(User).filter_by(id=login_session['user_id']).one()
    item = SESSION.query(Item).filter_by(id=message.item_id).one()
    if request.method == "POST":
        if user.id == message.receiver_id:
            new_message = Message(sender_id=login_session["user_id"],
                                  receiver_id=message.sender_id,
                                  item_id=message.item_id,
                                  message=request.form["message"])
            SESSION.add(new_message)
            SESSION.commit()
            flash("Reply sent")
            return redirect(url_for("show_user_messages"))
        flash("User not authorized")
        return redirect(url_for("show_user_messages"))
    return render_template("replymessage.html",
                           locations=locations,
                           message=message,
                           item=item)


@APP.route('/messages/<int:message_id>/delete', methods=['GET', 'POST'])
def delete_message(message_id):
    """ Delete selected message

    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    message = SESSION.query(Message).filter_by(id=message_id).one()
    user = SESSION.query(User).filter_by(id=login_session['user_id']).one()
    if request.method == 'POST':
        if user.id == message.receiver_id:
            SESSION.delete(message)
            SESSION.commit()
            flash('Message deleted')
            return redirect(url_for('show_user_messages'))
        flash('User not authorized')
        return redirect(url_for('show_user_messages'))
    return render_template('deletemessage.html',
                           locations=locations,
                           message=message)


@APP.route('/additem', methods=['GET', 'POST'])
def add_item():
    """ Add item to database.

    """

    # Check if user is logged in
    if 'email' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        new_item = Item(name=request.form['name'],
                        cardset=request.form['cardset'],
                        condition=request.form['condition'],
                        price=request.form['price'],
                        quantity=request.form['quantity'],
                        user_id=login_session['user_id'])
        SESSION.add(new_item)
        SESSION.commit()
        flash('Item added')
        return redirect(url_for('show_user_items'))
    return render_template('newitem.html')


@APP.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """ Edit selected item

    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    edited_item = SESSION.query(Item).filter_by(id=item_id).one()
    user = SESSION.query(User).filter_by(id=login_session['user_id']).one()
    if request.method == "POST":
        if user.id == edited_item.user_id:
            edited_item.name = request.form["name"]
            edited_item.cardset = request.form["cardset"]
            edited_item.condition = request.form["condition"]
            edited_item.quantity = request.form["quantity"]
            edited_item.price = request.form["price"]
            SESSION.add(edited_item)
            SESSION.commit()
            flash("Item changed")
            return redirect(url_for("show_user_items"))
        flash("User not authorized")
        return redirect(url_for("show_user_items"))
    return render_template("edititem.html",
                           locations=locations,
                           item=edited_item)


@APP.route('/items/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(item_id):
    """ Delete selected item

    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    deleted_item = SESSION.query(Item).filter_by(id=item_id).one()
    user = SESSION.query(User).filter_by(id=login_session['user_id']).one()
    if request.method == 'POST':
        if user.id == deleted_item.user_id:
            SESSION.delete(deleted_item)
            SESSION.commit()
            flash('Item deleted')
            return redirect(url_for('show_user_items'))
        flash('User not authorized')
        return redirect(url_for('show_user_items'))
    return render_template('deleteitem.html',
                           locations=locations,
                           item=deleted_item)


@APP.route('/')
def show_main():
    """ Main page showing the latest items.

    """

    locations = SESSION.query(Location).order_by(asc(Location.name))
    items = SESSION.query(Item).order_by(desc(Item.time_added)).limit(5)
    if 'email' not in login_session:
        return render_template('publicmain.html',
                               locations=locations,
                               items=items)
    return render_template('privatemain.html',
                           locations=locations,
                           items=items)


def create_user():
    """ Helper function to set up user log-in.

        Add user to database, return user id.
    """

    new_user = User(email=login_session['email'])
    SESSION.add(new_user)
    SESSION.commit()
    user = SESSION.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """ Helper function to set up user login.

        Return user information given user id.
    """

    user = SESSION.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    """ Helper function to set up user login.

        Return user id given email.
    """

    try:
        user = SESSION.query(User).filter_by(email=email).one()
        return user.id
    except RuntimeError:
        return None


if __name__ == '__main__':
    APP.secret_key = 'super_secret_key'
    APP.debug = True
    APP.run(host='0.0.0.0.xip.io', port=5000)
