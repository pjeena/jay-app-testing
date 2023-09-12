"""
    The code is used to extract data from MetaTrader5 using the "MetaTrader5" library 
    and store the data into a database using SQLAlchemy. The code uses a bulk insert 
    approach to insert the data more efficiently into the database. It also logs the 
    program's execution time and status to a log file.

"""
import pandas as pd
import numpy as np
from loguru import logger
import MetaTrader5 as mt5
from main_functions import *
import config as config

def load():

    # Get data from the MT5 platform using the get_mt5_data function
    df = extract_data_mt5()
    df = data_transformation(df)
    # Log the start of data insertion into the database
    logger.info("Start inserting data into {}")
    # Log the completion of data insertion and the successful completion of the program
    logger.info("Data extraction completed at {}".format(datetime.now()))
    logger.info("Program completed successfully.")
    df = df.sort_values(by = 'date', ascending=False)
    df.to_csv(config.FILE_PATH)
    return df

if __name__ == '__main__':

    setup_logging(config.LOG_PATH)
    df = load()
    print(df.head())