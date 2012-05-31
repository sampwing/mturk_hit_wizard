from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


from .models import DBSession, PageFactory, UserFactory

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    authentication = AuthTktAuthenticationPolicy(secret='lamesecret')
    aclauth = ACLAuthorizationPolicy()
    
    config = Configurator(settings=settings, authentication_policy=authentication, authorization_policy=aclauth)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/', factory=PageFactory)
    config.add_route('success', '/success', factory=PageFactory)
    
    config.add_route('login', '/login', factory=PageFactory)
    config.add_route('logout', '/logout', factory=PageFactory)

    config.add_route('view', '/view/{page_id}', factory=PageFactory)
    config.scan()
    return config.make_wsgi_app()

