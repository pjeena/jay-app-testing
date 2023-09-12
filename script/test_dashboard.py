import pandas as pd
#import dashboard as app
import plotly.graph_objs as go

import pandas as pd
import numpy as np
#from loguru import logger
from sqlalchemy import Column, Integer, Date, Float, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect
import psycopg2
from sqlalchemy import text
from datetime import datetime

# local files
from session import *
import run_query as q
from credential import postgresql as settings


def get_total_portfolio_growth() -> pd.DataFrame:
    
    query = """ SELECT 
                    date, 
                    SUM(profit) as growth
                FROM 
                    fx_tabtest
                GROUP BY
                    date
                ORDER BY 
                    date ASC"""
    result = q.run_query(query)
    
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

def Sessions():
    """
    Function to create the SQLAlchemy engine and session
    Returns:
        session object
    """
    #logger.info("Session Created")
    engine = get_engine_from_settings()
    Base.metadata.create_all(bind=engine)
    session = get_session()
    return session

#setup_logging('mt5_analysis.log')
Base = declarative_base()

# Create the SQLAlchemy engine and session
session = Sessions()

# SQL code for table creation
create_table_sql = """
CREATE TABLE IF NOT EXISTS fx_tabtest (
    id serial PRIMARY KEY,
    date DATE,
    profit DECIMAL(10, 2)
)
"""

# SQL code for inserting sample data
insert_data_sql = """
INSERT INTO fx_tabtest (date, profit)
VALUES
    ('2023-01-01', 100.50),
    ('2023-01-02', 150.25),
    ('2023-01-03', 200.75),
    ('2023-01-04', 50.00),
    ('2023-01-05', 300.80),
    ('2023-01-06', 75.50),
    ('2023-01-07', 180.30),
    ('2023-01-08', 250.10),
    ('2023-01-09', 120.90),
    ('2023-01-10', 90.60)
"""

try:
    # Execute the table creation SQL statement
    session.execute(text(create_table_sql))
    
    # Commit the transaction to save the changes to the database
    session.commit()
    
    # Execute the data insertion SQL statement
    session.execute(text(insert_data_sql))
    
    # Commit the transaction to save the changes to the database
    session.commit()
    
    logger.info("Table and sample data inserted successfully.")
    
except Exception as e:
    #logger.error(f"Error: {e}")
    session.rollback()

finally:
    session.close()



def test_get_total_portfolio_growth():
    # Test if the function returns a DataFrame
    result = get_total_portfolio_growth()
    assert isinstance(result, pd.DataFrame)

    # Add more specific tests if needed

def test_plot_growth_over_time():
    # Sample DataFrame for testing
    data = {'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'growth': [10, 15, 25]}
    df = pd.DataFrame(data)

    # Test if the function returns a Plotly Figure
    result = plot_growth_over_time(df, 'date', 'growth')
    assert isinstance(result, go.Figure)

