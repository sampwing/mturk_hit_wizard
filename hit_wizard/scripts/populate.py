import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    metadata,
    MyModel,
    User,
    Base,
    Data,
    Page
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)#, checkfirst=True)
    #metadata.create_all(engine)
    with transaction.manager:
        #model = MyModel(name='one', value=1)
        #DBSession.add(model)
        user = User(login='sam', password='sam')
        DBSession.add(user)

        data = Data(data_type=0, value='I like to have fun', gold=True, gold_value=True)
        DBSession.add(data)
        data = Data(data_type=0, value='I like to eat pancakes')
        DBSession.add(data)
        data = Data(data_type=0, value='I like to dance with monkeys')
        DBSession.add(data)
        data = Data(data_type=0, value="I enjoy jumping out of windows, when the risk of death is high.")
        DBSession.add(data)
        DBSession.flush()
        page = Page(data_type=0, name="Here is a bunch of happy stuff", description='Is this a happy thing?')
        DBSession.add(page)

