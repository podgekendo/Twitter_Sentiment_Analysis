__author__ = 'Padraig'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sqlalchemy as sa
from sqlalchemy import orm

import models


class SessionManager(object):
    """ Simple helper class, that creates and returns session object
    """
    def __init__(self, echo_mode=False):
        super(SessionManager, self).__init__()
		# os.path.sep used as the path separator
        DIR_PATH = os.path.dirname(__file__)
        db_path = DIR_PATH + os.path.sep + './tweet_sentiments.db'

        # MY engine_url directing to my sqlite database
        # http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
        engine_url = 'sqlite:///{0}'.format(
            db_path
        )
        self.engine = sa.create_engine(engine_url, encoding='utf-8', echo=echo_mode)

        # models.DeclBase.metadata.create_all(engine)
        # Set up the sessionmaker
        self.sm = orm.sessionmaker(bind=self.engine, autoflush=True, autocommit=False,
                              expire_on_commit=True)


    def createNewSession(self):
        return orm.scoped_session(self.sm)

def main():
    pass

if __name__ == '__main__':
    main()

