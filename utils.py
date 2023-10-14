import pandas as pd
import plotly.express as px
import plotly
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

mapping = {
    "hourly":"H",
    "daily":"D",
    "weekly":"W",
    "monthly":"M"
}

def get_plots(file_path):


    def update_trace(button):
            if button.label == 'Max':
                return [False, True, False]
            elif button.label == 'Min':
                return [False, False, True]
            elif button.label == 'Average':
                return [True, False, False]
            else:
                return [True, True, True]
                 
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    list_of_plots_json = []

    for item in mapping.items():
        state = item[0].capitalize()
        symbol = item[1]

        duration_avg = df['power'].resample(symbol).mean()
        duration_max = df['power'].resample(symbol).max()
        duration_min = df['power'].resample(symbol).min()

        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02)

        duration_avg_trace = go.Scatter(x=duration_avg.index, y=duration_avg.values, mode='lines', name=f'{state} Average Power Consumption')
        duration_max_trace = go.Scatter(x=duration_max.index, y=duration_max.values, mode='markers', name=f'{state} Max Power Consumption', marker=dict(size=8, color='red'))
        duration_min_trace = go.Scatter(x=duration_min.index, y=duration_min.values, mode='markers', name=f'{state} Min Power Consumption', marker=dict(size=8, color='green'))

        fig.add_trace(duration_avg_trace, row=1, col=1)
        fig.add_trace(duration_max_trace, row=1, col=1)
        fig.add_trace(duration_min_trace, row=1, col=1)

        buttons = [
            dict(label='Max', method='restyle', args=[{'visible': [False, True, False]}]),
            dict(label='Min', method='restyle', args=[{'visible': [False, False, True]}]),
            dict(label='Average', method='restyle', args=[{'visible': [True, False, False]}]),
            dict(label='All', method='restyle', args=[{'visible': [True, True, True]}])
        ]

        fig.update_xaxes(title_text="Timestamp", row=1, col=1)
        fig.update_yaxes(title_text=f"{state} Power Consumption", row=1, col=1)
        fig.update_layout(showlegend=True, updatemenus=[dict(type='buttons', showactive=True, buttons=buttons, x=1.20, y=0.6)], height=600)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        list_of_plots_json.append(graphJSON)
    
    return list_of_plots_json

def get_stats(file_path):
    df = pd.read_csv(file_path)
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

    return stats


async def delete_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"An error occurred while deleting the file: {str(e)}")