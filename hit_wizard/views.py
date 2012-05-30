from pyramid.view import view_config

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound

from pyramid.security import remember
from pyramid.security import forget

from .models import (
    DBSession,
    MyModel,
    User,
    )


@view_config(route_name='home', permission='home', renderer='templates/home.pt')
def my_view(request):
   login = authenticated_userid(request)
   if login:
      user = DBSession.query(User).filter(User.login==login).first()
      return {'user': user}   
   return {'user': None}


@view_config(route_name='success', permission='success', renderer='templates/success.pt')
def success_view(request):
   login = authenticated_userid(request)
   if login:
      user = DBSession.query(User).filter(User.login==login).first()
      return {'user': user}
   return {'user': None}


@view_config(route_name='logout', permission='logout')
def logout(request):
   headers = forget(request)
   home = request.route_url('home')
   return HTTPFound(location=home, headers=headers)

@view_config(route_name='login', permission='login', renderer='templates/login.pt')
def login_view(request):

   if authenticated_userid(request):
      success = request.route_url('success')
      return HTTPFound(location=success)
   login = ''

   did_fail = False
   
   next = request.params.get('next') or request.route_url('home')
   print "request.POST : ", request.POST
   if 'submit' in request.POST:
      login = request.POST.get('login', '') 
      password = request.POST.get('password', '')  

      user = DBSession.query(User).filter(User.login==login).first()
      print "user:", user
      print "dir:", dir(user)
      if user and user.user.check_password(password=password):
         headers = remember(request, login)

         success = request.route_url('success')
         return HTTPFound(location=success, headers=headers)
      did_fail = True

   return {
      'user': None,
      'login': login,
      'failed_attempt': did_fail,
      'results': ''
   }   

