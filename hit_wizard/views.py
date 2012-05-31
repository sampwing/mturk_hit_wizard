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
    Page,
    Data,
    Annotation
    )




@view_config(route_name='view', permission='home', renderer='templates/view.pt')
def view(request):
    page_id = request.matchdict['page_id']
    page = DBSession.query(Page).filter(Page.id==page_id).first()
    print page
    data = DBSession.query(Data).filter(Data.data_type==page.data_type).all()
    print data
    return {'user': None, 'data': data, 'page': page}


@view_config(route_name='home', permission='home', renderer='templates/home.pt')
def my_view(request):
    page = DBSession.query(Page).first()
    print page
    data = DBSession.query(Data).filter(Data.data_type==page.data_type).all()
    print data
    return {'user': None, 'data': data, 'page': page}


@view_config(route_name='success', permission='success', renderer='templates/success.pt')
def success_view(request):
   login = authenticated_userid(request)
   if login:
      user = DBSession.query(User).filter(User.login==login).first()
      pages = DBSession.query(Page).all()
      return {'user': user, 'pages': pages}
   return {'user': None, 'pages': pages}


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

