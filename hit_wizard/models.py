from sqlalchemy import (
    Column,
    Integer,
    Text,
    PickleType,
    ForeignKey,
    Boolean
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import Everyone
from pyramid.security import Allow
from pyramid.security import Authenticated


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class PageFactory(object):
   __acl__ = [
      (Allow, Everyone, 'home'),
      (Allow, Everyone, 'login'),
      (Allow, Authenticated, 'success'),
      (Allow, Authenticated, 'logout'),
   ]

   def __init__(self, request):
      self.request = request

class UserFactory(PageFactory):
   
   def __getitem__(self, key):
      user = DBSession.query(User).filter(User.login==key).first()
      if user:
         return user.user
      return None
   
 

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

  
class UserObject(object):
   @property
   def __acl__(self):
      return [
         (Allow, self.login, 'view')
      ]

   def __init__(self, login=None, password=None):
      self.login = login
      self.password = password

   def check_password(self, password=None):
      return self.password == password

class User(Base):
   __tablename__ = 'users'

   id = Column(Integer, primary_key=True)
   login = Column(Text, unique=True)
   user = Column(PickleType)

   def __init__(self, login, password):
      self.login = login
      self.user = UserObject(login=login, password=password)


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, autoincrement=True, primary_key=True)
    data_type = Column(Integer)
    value = Column(Text)
    range_lower = Column(Integer)
    range_upper = Column(Integer)
    gold = Column(Boolean)

    def __init__(self, data_type, value, range_lower=0, range_upper=0, gold=False):
        self.data_type = data_type
        self.value = value
        self.range_lower = range_lower
        self.range_upper = range_upper
        self.gold = gold

    def is_bool(self):
        return self.range_lower == self.range_upper

    def is_gold(self):
        return self.gold

    def __repr__(self):
        return "<{} {} {} {}>".format(self.__tablename__, self.id, self.data_type, self.value)


class Annotation(Base):
    __tablename__ = 'annotation'
    id = Column(Integer, autoincrement=True, primary_key=True)
    data_type = Column(Integer, ForeignKey('data.data_type'))
    value = Column(Integer, ForeignKey('data.value'))
    result = Column(Boolean)

    def __init__(self, data_type, value, result):
        self.data_type = data_type
        self.value = value
        self.result = result


class Page(Base):
    __tablename__ = 'page'
    id = Column(Integer, autoincrement=True, primary_key=True)
    data_type = Column(Integer, ForeignKey('data.data_type'))
    description = Column(Text)
    annotations_per_page = Column(Integer)
    uses_gold = Column(Boolean)

    def __init__(self, data_type, description='default description', annotations_per_page=1, uses_gold=False):
        self.data_type = data_type
        self.description = description
        self.annotations_per_page = annotations_per_page
        self.uses_gold = uses_gold

    def __repr__(self):
        return "<{} {} {}>".format(self.__tablename__, self.data_type, self.description)

