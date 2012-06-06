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
    Data,
    Page,
    Annotation
    )


@view_config(route_name='record', permission='success')
def record_annotations(request):
    import re
    page_id = request.POST['page_id']
    for key in request.POST:
        result = re.search(r'option_([0-9]+)', key)
        if not result: continue




@view_config(route_name='save', permission='success')
def save_data(request):
    name = request.POST['name']
    description = request.POST['description']
    perpage = int(request.POST['perpage'])
    data_name = request.POST['data'].filename
    data_file = request.POST['data'].file
    print name, description, data_name
    #process the data_file as a csv and load it into the database
    import csv
    reader = csv.reader(data_file, delimiter=',')

    type_id = 1
    for row in reader:
        data = Data(data_type=type_id, value=row[0])
        DBSession.add(data)
    page = Page(data_type=type_id, name=name, description=description, annotations_per_page=perpage)
    DBSession.add(page)
    url = request.route_url('success')
    return HTTPFound(location=url)


@view_config(route_name='create', permission='success', renderer='templates/create.pt')
def create_page(request):
    login = authenticated_userid(request)
    if login:
        user = DBSession.query(User).filter(User.login==login).first()
        return {'user': user}
    return {'user': None}


@view_config(route_name='delete', permission='success')
def delete_page(request):
    page_id = request.matchdict['page_id']
    page = DBSession.query(Page).filter(Page.id==page_id).first()
    DBSession.delete(page)
    success = request.route_url('success')
    return HTTPFound(location=success)

@view_config(route_name='view', permission='success', renderer='templates/view.pt')
def view(request):
    page_id = request.matchdict['page_id']
    page = DBSession.query(Page).filter(Page.id==page_id).first()
    data = DBSession.query(Data).filter(Data.data_type==page.data_type).all()
    # XXX lets limit it to only showing the first 5 items for testing the annotations
    data = data[:5]
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

