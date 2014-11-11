#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import sqlalchemy as sa
from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint,
    )

import models


class SchemaManager(object):
    def __init__(self, echo_mode=False):
        super(SchemaManager, self).__init__()
		### To get the dir-name of the absolute path
        DIR_PATH = os.path.dirname(__file__)
        db_path = DIR_PATH + os.path.sep + './tweet_sentiments.db'
        engine_url = 'sqlite:///{0}'.format(
            db_path
        )
        self.engine = sa.create_engine(engine_url, encoding='utf-8', echo=echo_mode)


    def create_db_schema(self):
        decl_base = models._getDeclBase()
        decl_base.metadata.create_all(self.engine)

    def drop_db_schema(self):
        ### receipt to drop everything
        ### https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
        ### trans only applies if the db supports
        conn = self.engine.connect()
        trans = conn.begin()
		### Gather all the data before dropping anything
        inspector = reflection.Inspector.from_engine(self.engine)
        metadata = MetaData()

        tbs = []
		### foreign keys mysqlite
        all_fks, fks = [], []

		### quick path to all table / fk names, use an inspector:
        for table_name in inspector.get_table_names():
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(
                    ForeignKeyConstraint((),(),name=fk['name'])
                )

            t = Table(table_name,metadata,*fks)
            tbs.append(t)
            all_fks.extend(fks)

        for fkc in all_fks:
            conn.execute(DropConstraint(fkc))

        for table in tbs:
            conn.execute(DropTable(table))

        trans.commit()
        

if __name__ == '__main__':
    pass

