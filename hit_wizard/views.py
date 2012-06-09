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

from sqlalchemy import desc, func, distinct


@view_config(route_name='record')
def record_annotations(request):
    import re
    import random
    page_id = request.POST['page_id']
    random_identifier = int(random.random() * 100000) #to be used until you can uniquely id them

    passed_gold_test = False

    for key in request.POST:
        result = re.search(r'gold_([0-9]+)', key)
        if result:
            gold_value = True if request.POST[key] == 'Yes' else False
            #check whether this value is accurate
            gold_data = DBSession.query(Data).filter(Data.id==result.group(1)).first()
            passed_gold_test = (gold_data.gold_value == gold_value)
            print 'RESULT:{}'.format(passed_gold_test)
            continue
        result = re.search(r'option_([0-9]+)', key)
        if not result: continue
        data_id = result.group(1)
        bool = True if request.POST[key] == 'Yes' else False
        annotation = Annotation(random_identifier=random_identifier, page_id=page_id, data_id=data_id, result=bool)
        DBSession.add(annotation)

    #if passed_gold_test offer more pages to annotate, offer reward for bonus pages
    if passed_gold_test:
        url = request.route_url('view', page_id=page_id)
        return HTTPFound(location=url)
    url = request.route_url('home')
    return HTTPFound(location=url)



@view_config(route_name='save', permission='success')
def save_data(request):
    import csv

    name = request.POST['name']
    description = request.POST['description']
    try:
        perpage = int(request.POST['perpage'])
    except ValueError:
        perpage = 5 #DEFAULTVALUE

    data_name = request.POST['data'].filename
    data_file = request.POST['data'].file

    gold_name = request.POST['gold'].filename
    gold_file = request.POST['gold'].file

    print name, description, data_name, gold_name

    page = DBSession.query(Page).order_by(desc(Page.data_type)).first()
    type_id = page.data_type + 1

    #process the data_file as a csv and load it into the database
    reader = csv.reader(data_file, delimiter=',')
    for row in reader:
        if not row: break
        data = Data(data_type=type_id, value=row[0])
        DBSession.add(data)

    #process the data_file as a csv and load it into the database
    reader = csv.reader(gold_file, delimiter=',')
    for row in reader:
        if not row: break
        boolean = True if row[0] == 'TRUE' else False
        data = Data(data_type=type_id, value=row[0], gold=True, gold_value=boolean)
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

@view_config(route_name='view', renderer='templates/view.pt')
def view(request):
    import random
    page_id = request.matchdict['page_id']
    page = DBSession.query(Page).filter(Page.id==page_id).first()
    data = DBSession.query(Data).filter(Data.data_type==page.data_type).filter(Data.gold==False).all()
    # XXX lets limit it to only showing the first 5 items for testing the annotations
    gold = random.choice(DBSession.query(Data).filter(Data.data_type==page.data_type).filter(Data.gold==True).all())
    data = random.sample(data, page.annotations_per_page)#data[:5]
    return {'user': None, 'data': data, 'page': page, 'gold': gold}


@view_config(route_name='home', permission='home', renderer='templates/home.pt')
def my_view(request):
    login = authenticated_userid(request)
    user = None
    if login:
        user = DBSession.query(User).filter(User.login==login).first()
    pages = DBSession.query(Page).all()
    return {'pages': pages, 'user': user}


@view_config(route_name='success', permission='success', renderer='templates/success.pt')
def success_view(request):
    from collections import defaultdict
    import nltk

    login = authenticated_userid(request)
    if login:
        user = DBSession.query(User).filter(User.login==login).first()
        pages = DBSession.query(Page).all()
        kappa = defaultdict(int)
        annotators = defaultdict(int)

        for page in pages:
            annotators[page.id], = DBSession.query(func.count(distinct(Annotation.random_identifier))).filter(Annotation.page_id==page.id).first()
            print 'annotators:{}'.format(annotators)
            annotations = DBSession.query(Annotation).filter(Annotation.page_id==page.id).all()

            try:
                data = [(annotation.random_identifier, annotation.data_id, annotation.result) for annotation in annotations]
                agreement = nltk.metrics.agreement.AnnotationTask(data=data)
                kappa[page.id] = agreement.kappa()
            except ZeroDivisionError, e:
                print data, e
        return {'user': user, 'pages': pages, 'kappa': kappa}
    return HTTPForbidden()


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

