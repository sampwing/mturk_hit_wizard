from sqlalchemy import (
    Column,
    Integer,
    Text,
    PickleType,
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

