# Import SQLAlchemy dependencies
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

# Import empty database we created in database_setup.py
from database_setup import Base, User, Category, Item

# Let our program know which database engine we want to communicate with
engine = create_engine('sqlite:///catalog.db')

# Bind engine to Base class so declaratives can be accessed through DBSession
Base.metadata.bind = engine

# Sessionmaker establishes communication between code and engine
DBSession = sessionmaker(bind=engine)

# Establishes link with database. Changes in the session won't be in the
# database until call to session.commit()
session = DBSession()

# Add users to database
User1 = User(name="Person A", email="person_a@udacity.com")
session.add(User1)
session.commit()

User2 = User(name="Person B", email="person_b@udacity.com")
session.add(User2)
session.commit()

User3 = User(name="Person C", email="person_c@udacity.com")
session.add(User3)
session.commit()

User4 = User(name="Person D", email="person_d@udacity.com")
session.add(User4)
session.commit()

User5 = User(name="Person E", email="person_e@udacity.com")
session.add(User5)
session.commit()

# Add locations
Category1 = Category(name="GP Vegas")
session.add(Category1)
session.commit()

Category2 = Category(name="GP San Jose")
session.add(Category2)
session.commit()

# Add items to database
Item11 = Item(name="Glistener Elf",
              description="NM/M",
              time_added=datetime.datetime.utcnow(),
              category_id=1,
              user_id=1)
session.add(Item11)
session.commit()

Item12 = Item(name="Blighted Agent",
              description="MP",
              time_added=datetime.datetime.utcnow(),
              category_id=1,
              user_id=2)
session.add(Item12)
session.commit()

Item24 = Item(name="Might of Old Krosa",
              description="PL",
              time_added=datetime.datetime.utcnow(),
              category_id=2,
              user_id=4)
session.add(Item24)
session.commit()

print "Added user, categories and items!"
