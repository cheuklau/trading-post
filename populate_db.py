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

# Add categories to database
Category1 = Category(name="Category 1")
session.add(Category1)
session.commit()

Category2 = Category(name="Category 2")
session.add(Category2)
session.commit()

Category3 = Category(name="Category 3")
session.add(Category3)
session.commit()

Category4 = Category(name="Category 4")
session.add(Category4)
session.commit()

Category5 = Category(name="Category 5")
session.add(Category5)
session.commit()

# Add items to database
Item11 = Item(name="Item 11",
              description="This is Item 11",
              time_added=datetime.datetime.utcnow(),
              category_id=1,
              user_id=1)
session.add(Item11)
session.commit()

Item12 = Item(name="Item 12",
              description="This is Item 12",
              time_added=datetime.datetime.utcnow(),
              category_id=1,
              user_id=2)
session.add(Item12)
session.commit()

Item13 = Item(name="Item 13",
              description="This is Item 13",
              time_added=datetime.datetime.utcnow(),
              category_id=1,
              user_id=3)
session.add(Item13)
session.commit()

Item24 = Item(name="Item 24",
              description="This is Item 24",
              time_added=datetime.datetime.utcnow(),
              category_id=2,
              user_id=4)
session.add(Item24)
session.commit()

Item32 = Item(name="Item 32",
              description="This is Item 32",
              time_added=datetime.datetime.utcnow(),
              category_id=3,
              user_id=2)
session.add(Item32)
session.commit()

Item35 = Item(name="Item 35",
              description="This is Item 35",
              time_added=datetime.datetime.utcnow(),
              category_id=3,
              user_id=5)
session.add(Item35)
session.commit()

Item41 = Item(name="Item 41",
              description="This is Item 41",
              time_added=datetime.datetime.utcnow(),
              category_id=4,
              user_id=1)
session.add(Item41)
session.commit()

Item42 = Item(name="Item 42",
              description="This is Item 42",
              time_added=datetime.datetime.utcnow(),
              category_id=4,
              user_id=2)
session.add(Item42)
session.commit()

Item45 = Item(name="Item 45",
              description="This is Item 45",
              time_added=datetime.datetime.utcnow(),
              category_id=4,
              user_id=5)
session.add(Item45)
session.commit()

print "Added user, categories and items!"
