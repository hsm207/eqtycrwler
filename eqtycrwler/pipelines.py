# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from dbmodel import Profiles, db_connect, create_profiles_table
from scrapy.exceptions import DropItem


# Pipeline to insert scraped item into db
class DbPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_profiles_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        profile = Profiles(**item)

        try:
            session.add(profile)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item


# Pipeline to handle 'None' profile
class NoneProfilePipeline(object):
    def process_item(self, item, spider):
        if item['yhoo_profile'] is None:
            item['yhoo_profile'] = 'Data not available :('
            item['profile_link'] = 'Data not available :('
        return item


# Pipeline to check that we aren't inserting duplicate values into the db
class ScrapedPipeline(object):
    def __init__(self):
        engine = db_connect()
        session = sessionmaker(bind=engine)()
        self.keys = session.query(Profiles.code, Profiles.yhoo_profile)
        session.close()

    def process_item(self, item, spider):
        code, profile = item['code'], item['yhoo_profile']
        if (code, profile) in self.keys:
            raise DropItem("The following Item is already in the db:")
        else:
            return item
