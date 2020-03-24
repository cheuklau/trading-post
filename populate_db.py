"""
Populate postgresql database for testing
"""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import empty database we created in database_setup.py
from database_setup import Base, User, Location, Item, Message

# Let our program know which database engine we want to communicate with
ENGINE = create_engine('sqlite:///catalog.db')

# Bind engine to Base class so declaratives can be accessed through DBSession
Base.metadata.bind = ENGINE

# Sessionmaker establishes communication between code and engine
DBSESSION = sessionmaker(bind=ENGINE)

# Establishes link with database. Changes in the session won't be in the
# database until call to session.commit()
SESSION = DBSESSION()

# Add users to database
SESSION.add(User(email="john_smith@email.com", location_id=1))
SESSION.add(User(email="jane_doe@email.com", location_id=1))
SESSION.add(User(email="jack_daniels@email.com", location_id=2))

# Add locations to database
SESSION.add(Location(name="GP Vegas"))
SESSION.add(Location(name="GP San Jose"))

# Add items to database
SESSION.add(Item(
    user_id=1,
    name="Black Lotus",
    cardset="Alpha",
    condition="Near Mint",
    price="100.00",
    quantity="1",
    time_added=datetime.datetime.utcnow()))
SESSION.add(Item(
    user_id=1,
    name="Aether Vial",
    cardset="Kaladesh",
    condition="Lightly Played",
    price="50.00",
    quantity="1",
    time_added=datetime.datetime.utcnow()))
SESSION.add(Item(
    user_id=2,
    name="Liliana of the Veil",
    cardset="Modern Masters",
    condition="Heavily Played",
    price="10.25",
    quantity="1",
    time_added=datetime.datetime.utcnow()))
SESSION.add(Item(
    user_id=3,
    name="Mox Opal",
    cardset="Scars of Mirrodin",
    condition="Damaged",
    price="1.00",
    quantity="1",
    time_added=datetime.datetime.utcnow()))

# Add messages
SESSION.add(Message(
    sender_id=1,
    receiver_id=2,
    item_id=2,
    message="I want that Mox Ruby!"
))

# Commit session
SESSION.commit()

print "Added user, locations, items and messages!"
