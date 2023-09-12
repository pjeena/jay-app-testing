import os
import MetaTrader5 as mt5
from datetime import datetime, date
from typing import List, Dict
import pandas as pd
from loguru import logger
from credential import mt5_credentials
import plotly.express as px
import plotly.graph_objects as go


def setup_logging(log_file):
    """
    Set up logging to a file.

    Args:
        log_file (str): The path to the log file.

    Returns:
        None
    """
    logger.remove()  # Remove any previously added log handlers
    logger.add(log_file, rotation="1 day", level="INFO")

def extract_data_mt5() -> pd.DataFrame:
    
    """This function extracts historical trade data from the mt5 platform using MT5 API!"""

    # establish MetaTrader 5 connection to a specified trading account

    if not mt5.initialize():
        logger.info("initialize() failed, error code: %s",mt5.last_error())
        quit()
    mt5.login(login=mt5_credentials['login'], server=mt5_credentials['server'],password=mt5_credentials['password'])
    
    pd.set_option('display.max_columns', 500) # number of columns to be displayed
    pd.set_option('display.width', 1500)      # max table width to display

    # display data on the MetaTrader 5 package
    logger.info("MetaTrader5 package author: %s", mt5.__author__)
    logger.info("MetaTrader5 package version: %s", mt5.__version__)

    from_date=datetime(2023,9,1)
    to_date=datetime.now()

    # get deals for symbols whose names contain "GBP" within a specified interval
    deals=mt5.history_deals_get(from_date, to_date)

    if deals==None:
        error_code = mt5.last_error()
        logger.warning("No deals found, error code = %d", error_code)
        
    elif len(deals)> 0:
        logger.info("history_deals_get(%s, %s) = %d", from_date, to_date, len(deals))
        # display these deals as a table using pandas.DataFrame
        df=pd.DataFrame(list(deals),columns=deals[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
            #logging.info("\n%s", df)
        #return df
    return df  
    # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()


def data_transformation(df: pd.DataFrame) -> pd.DataFrame:
 
    """
    Split a DataFrame's 'time' column into separate 'date' and 'time' columns,
    and create a new DataFrame with selected columns for report analysis.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'time' column.
    resutn:
        pd.DataFrame: A new DataFrame with 'date' and selected columns for analysis.
    """

    logger.info("Data transformation in process ....")
    # Convert 'time' column to string type
    df['time'] = df['time'].astype(str)

    # Split the 'time' column into 'date' and 'time'
    date_time_split = df['time'].str.split(expand=True)
    date_time_split = date_time_split.rename(columns={0: "date", 1: "time"})
    df.insert(2, 'date', date_time_split['date'])

    # Create a new DataFrame with selected columns for analysis
    selected_columns = [
        'date', 'type', 'volume', 'commission', 'swap', 'profit', 'fee', 'symbol'
    ]
    df_report_analysis = df[selected_columns]
    logger.info("Data transformation done!")
    return df_report_analysis


def get_total_portfolio_growth(df) -> pd.DataFrame:
    

    df['date'] = pd.to_datetime(df['date'])

    # Perform the SQL-like query using Pandas
    result_df = df.loc[df['type'] != 2]
    result_df = result_df.groupby('date')['profit'].sum().reset_index()
    result_df.columns = ['date', 'growth']
    result_df = result_df.sort_values(by='date')

    # Print the result
    
    logger.info("data transformed to required format!")
    return result_df


def deposits(df: pd.DataFrame, type_value: int = 2) -> pd.DataFrame:
    
    """
    Filter a DataFrame by a specific 'type' value and return a new DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame to be filtered.
        type_value (int): The 'type' value to filter by.

    Returns:
        pd.DataFrame: A new DataFrame containing rows where the 'type' column matches the specified value.
    """
    filtered_df = df[df['type'] == type_value]
    columns = ['date', 'type', 'profit']
    filtered_df = filtered_df[columns]
    filtered_df = filtered_df.rename(columns = {'profit':'deposit'})
    logger.info('deposit table is ready!')
    return filtered_df

def total_profits() -> pd.DataFrame:
    """
    Calculate the total profit for each unique ID in the 'fx_history' table.

    Returns:
        pd.DataFrame: A DataFrame containing the results with total profit calculated.
    """
    # """ #
    # define the SQL query to be executed
    query = """SELECT 
                    *, 
                    SUM(commission + swap + profit) AS total_profit 
                FROM 
                    fx_history 
                WHERE 
                    type != 2 
                GROUP BY 
                id
                ORDER BY 
                date ASC"""

    # call the run_query function with the SQL query
    result = run_query(query)
    #logger.info(result_df) 
    return result


def plot_growth_over_time(dataframe: pd.DataFrame, 
                            x_column: str, 
                            y_column: str,
                            title: str = "Growth Over Time") -> go.Figure:
    
    """
    Plot a line plot with scatter points to visualize growth over time.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing the data.
    x_column (str): The name of the column containing date values.
    y_column (str): The name of the column containing growth values.
    title (str, optional): The title of the plot (default is "Growth Over Time").

    Returns:
    fig (plotly.graph_objs.Figure): The Plotly figure object.
    """

    fig = go.Figure()

    # Create a line plot
    fig.add_trace(go.Scatter(x=dataframe[x_column], y=dataframe[y_column], mode='lines', name='Line'))

    # Add scatter points
    fig.add_trace(go.Scatter(x=dataframe[x_column], y=dataframe[y_column], mode='markers', name='Scatter'))

    # Customize the layout
    fig.update_layout(title=title,
                    xaxis_title="Date",
                    yaxis_title="Growth",
                    showlegend=True)

    return fig



    
