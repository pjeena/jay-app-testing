import sys
sys.path.append('script/')
import install_env as install_env

import pandas as pd
import streamlit as st
# from bokeh.models import Div
import plotly.express as px
import plotly.graph_objects as go
#from main_functions import *
import config as config


# building env and installing requirements.txt



def get_total_portfolio_growth(df) -> pd.DataFrame:


    df['date'] = pd.to_datetime(df['date'])

    result_df = df.loc[df['type'] != 2]
    result_df['total_profit'] = result_df['profit']+result_df['swap']   + result_df['commission'] + result_df['fee']
    result_df = result_df.groupby('date')['total_profit'].sum().reset_index()
    result_df.columns = ['date', 'growth']
    result_df = result_df.sort_values(by='date', ascending = False )

    # Print the result
    
    return result_df

def plot_growth_over_time(dataframe: pd.DataFrame, 
                            x_column: str, 
                            y_column: str,
                            title: str = "Growth Over Time") -> go.Figure:
    
    
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

    
    install_env.create_environment()

    
    st.title('My Forex Dashboard 2023')

    df = pd.read_csv(config.FILE_PATH)
    #logger.info("Connection to dashboard is established!")
    growth_df = get_total_portfolio_growth(df)
    st.dataframe(growth_df, use_container_width = True)

    

    growthplot = plot_growth_over_time(growth_df, 'date', 'growth', title="Growth Over Time")
    st.plotly_chart(growthplot)
