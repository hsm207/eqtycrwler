from sqlalchemy import create_engine, Column, String, BigInteger, DateTime
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import settings

# Need this to associate our python classes to the tables in postgres
DeclarativeBase = declarative_base()


def db_connect():
    return create_engine(URL(**settings.DATABASE))  # '**' means unpack content of dictionary into a sequence


def create_profiles_table(engine):
    DeclarativeBase.metadata.create_all(engine)


# define the table in postgres in terms of a python class
# attributes must match the corresponding item
class Profiles(DeclarativeBase):
    __tablename__ = "profiles"

    code = Column('code', String, primary_key=True)
    short_name = Column('short_name', String, nullable=False)
    yhoo_profile = Column('profile', String, nullable=True, primary_key=True)
    bursa_profile = Column('exchange_link', String, nullable=False)
    profile_link = Column('profile_link', String, nullable=True)
    row_num = Column('row_num', BigInteger, nullable=False)
    scrape_time = Column('scrape_time_gmt', DateTime, nullable=False)
