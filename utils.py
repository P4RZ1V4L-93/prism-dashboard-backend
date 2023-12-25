import pandas as pd
import plotly.express as px
import plotly
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from collections import Counter
from plots import get_aggregate_plots, get_night_and_slope_highlight_plot, get_weekday_plots


def get_plots(data_frame: pd.DataFrame):

    '''
        Generates various types of plots based on power consumption data.
    '''

    df = data_frame.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    plots_json = {}
    weekday_plots_json = get_weekday_plots(df)
    aggregate_plots_json = get_aggregate_plots(df)
    night_and_slope_highlighted_plots_json = get_night_and_slope_highlight_plot(df)
    plots_json.update(aggregate_plots_json)
    plots_json.update(weekday_plots_json)
    plots_json.update(night_and_slope_highlighted_plots_json)
    return plots_json


def get_stats(df: pd.DataFrame):

    '''
        Calculates various statistical measures for power consumption data.
    '''

    stats_df = df["power"].describe()
    median = df["power"].median()
    stats = {
        "count": stats_df["count"],
        "mean": stats_df["mean"],
        "std": stats_df["std"],
        "min": stats_df["min"],
        "percentile_25": stats_df["25%"],
        "percentile_50": stats_df["50%"],
        "percentile_75": stats_df["75%"],
        "max": stats_df["max"],
        "median": median
    }

    return stats


async def delete_file(file_path):

    '''
        Asynchronously attempts to delete a file.
    '''

    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"An error occurred while deleting the file: {str(e)}")
