'''
    This script is used to initially configure the redis with statistics and plots of distinct devices.
'''

# Import necessary Dependency
from models import categories
import pandas as pd
from database import engine
import plotly.express as px
import json
import redis
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_plots, get_stats


redis_client = redis.Redis(host='localhost', port=6379, db=0)

# function to save plot as json format in redis
def savePlot(category_name):
    
    df = pd.read_sql_table(table_name=f"{category_name}_power_consumption", con=engine)    
    list_of_plots_json = get_plots(df)
    redis_client.set(f'{category_name}_plot', json.dumps(list_of_plots_json))

# function to store statistics in the redis 
def saveStatistics(category_name):
    
    df = pd.read_sql_table(
        table_name=f"{category_name}_power_consumption", con=engine)
    stats = get_stats(df)
    redis_client.set(f'{category_name}_statistics', str(stats))

# function to save statistics and plots for available categories of devices
def saveData():
    
    for category in categories:        
        # saveStatistics(category)
        savePlot(category)

# saveData()