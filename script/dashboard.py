import streamlit as st
import pandas as pd
import run_query as q
import plotly.express as px
import plotly.graph_objects as go

from loguru import logger

#@st.cache_data
def get_total_portfolio_growth(df: pd.DataFrame) -> pd.DataFrame:

    # Convert the 'date' column to datetime if it's not already
    df['date'] = pd.to_datetime(df['date'])

    # Perform the SQL-like query using Pandas
    result_df = result_df.loc[result_df['type'] != 2]
    result_df = df.groupby('date')['profit'].sum().reset_index()
    result_df.columns = ['date', 'growth']
    result_df = result_df.sort_values(by='date')

    # Print the result
    
    logger.info("data transformed to required format!")
    return result_df


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


if __name__ == '__main__':

    st.title('My Forex Dashboard 2023')
    logger.info("Connection to dashboard is established!")
    growth_df = get_total_portfolio_growth()
    st.dataframe(growth_df, use_container_width = True)

    growthplot = plot_growth_over_time(growth_df, 'date', 'growth', title="Growth Over Time")
    st.plotly_chart(growthplot)
