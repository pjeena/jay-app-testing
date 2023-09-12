import pandas as pd
import numpy as np
from loguru import logger
from sqlalchemy import Column, Integer,Date, Float, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect
import psycopg2
from sqlalchemy import text
# local files
from session import *
from main_functions import *
from run_query import *
from credential import postgresql as settings


def Sessions():
    """
    Function to create the SQLAlchemy engine and session
    Returns:
        session object
    """
    logger.info("Session Created")
    engine = get_engine_from_settings()
    Base.metadata.create_all(bind=engine)
    session = get_session()
    return session

def create_table(table_name, Base):
    """
    Function to create table structure using SQLAlchemy ORM
    Args:
        table_name : name of the table to be created
        Base       : SQLAlchemy Base object
        engine     : SQLAlchemy engine object
    Returns:
        User       : SQLAlchemy ORM Class for the table
    """
    engine = get_engine_from_settings()
    class User(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, autoincrement=True)
        date = Column(Date)
        total_volume = Column(Float)
        profit_per_symbol = Column(Float)
        cumulative_percentage_gain_per_symbol = Column(Float)
        symbol = Column(String(255))

    inspector = inspect(engine)
    #if engine.has_table(table_name):
    if inspector.has_table(table_name):
        # if table exists, overwrite it
        User.__table__.drop(engine)
        User.__table__.create(engine)
    else:
        # if table does not exist, create it
        Base.metadata.create_all(engine)
        
    return User


def load(Base):
    
    name = 'fx'+'_'+'totalprofit'
    table_name = name
    # Create SQLAlchemy Base object and User class using the create_table function
    #Base = declarative_base()
    User = create_table(table_name, Base)
    logger.info('Table Created!')
    # Create a SQLAlchemy session
    session = Sessions()
    # Get data from the MT5 platform using the get_mt5_data function
    df = total_profits()
    # Log the start of data insertion into the database
    logger.info("Start inserting data into {}".format(table_name))
    # Insert the data into the database using the bulk_insert_mappings method
    session.bulk_insert_mappings(User,df.to_dict(orient='records'))
    # Commit the transaction to save the changes to the database
    session.commit()
    # Log the completion of data insertion and the successful completion of the program
    logger.info("Data insertion completed at {}".format(datetime.now()))
    logger.info("Program completed successfully.")

if __name__ == '__main__':

    setup_logging('mt5_analysis.log')
    Base = declarative_base()
    load(Base)