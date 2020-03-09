# Bind code to the SQLAlchemy engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

# Create base class for classes to inherit SQLAlchemy properties
Base = declarative_base()

class Location(Base):
    """ Create location table

        Attributes:
            id: An integer acting as the primary key
            name: A string representing name of the location
    """

    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class User(Base):
    """ User table

        Attributes:
            id: An integer acting as the primary key
            name: A string representing name of the user
            email: A string represeting email of the user
            location: A string representing location of the user
    """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('location.id'))
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    location = relationship(Location)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'location_id': self.location_id,
            'name': self.name,
            'email': self.email
        }


class Item(Base):
    """ Create item table

        Attributes:
            id: An integer acting as the primary key
            user_id: Integer foreign key of person adding the card
            name: A string representing the name of the item
            cardset: A string representing the set of the card
            condition: A string representing card condition
            price: A float representing asking price of card
            quantity: An integer representing quantity of card
            time_added: A datetime representing time card was added
    """

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(250), nullable=False)
    cardset = Column(String(250), nullable=False)
    condition = Column(String(250), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    time_added = Column(DateTime, default=datetime.datetime.utcnow())
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'cardset': self.cardset,
            'condition': self.condition,
            'price': self.price,
            'quantity': self.quantity,
            'time_added': self.time_added
        }


class Message(Base):
    """ Create message table

        Attributes:
            id: An integer acting as the primary key
            sender_id: An integer representing the person sending the message
            receiver_id: An integer representing the person receiving the message
            item_id: An integer representing the item this message is about
            message: A string representing the message
    """

    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('user.id'))
    receiver_id = Column(Integer, ForeignKey('user.id'))
    item_id = Column(Integer, ForeignKey('item.id'))
    message = Column(String(250), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    item = relationship(Item)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'item_id': self.item_id,
            'message': self.message
        }

# Final configuration code
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)