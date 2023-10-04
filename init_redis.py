'''
    This script is used to initially configure the redis with statistics and plots of distinct devices.
'''

# Import necessary Dependency
from models import categories
import pandas as pd
from database import engine
import plotly.express as px
import plotly
import json
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
# function to save plot as json format in redis
def savePlot(category_name):
    df = pd.read_sql_table(table_name=f"{category_name}_power_consumption", con=engine)    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df_5min = df.power.resample('5T').mean()
    fig = px.line(x=df_5min.index, y=df_5min.values, title='Power Consumption Plot')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    redis_client.set(f'{category_name}_plot', str(graphJSON))

# function to store statistics in the redis 
def saveStatistics(category_name):
    df = pd.read_sql_table(
        table_name=f"{category_name}_power_consumption", con=engine)

    stats_df = df["power"].describe()
    median = df["power"].median()
    stats = {
        "count":stats_df["count"],
        "mean":stats_df["mean"],
        "std":stats_df["std"],
        "min":stats_df["min"],
        "percentile_25":stats_df["25%"],
        "percentile_50":stats_df["50%"],
        "percentile_75":stats_df["75%"],
        "max":stats_df["max"],
        "median":median
    }

    redis_client.set(f'{category_name}_statistics', str(stats))

# function to save statistics and plots for available categories of devices
def saveData():
    for category in categories:        
        saveStatistics(category)
        savePlot(category)

# saveData()