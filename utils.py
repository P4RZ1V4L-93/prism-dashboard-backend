import pandas as pd
import plotly.express as px
import plotly
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from collections import Counter

# time_interval_mapping is a dictionary that maps human-readable time intervals to their corresponding string representations.
time_interval_mapping = {
    "hourly": "H",
    "daily": "D",
    "weekly": "W",
    "monthly": "M"
}

# month_dict is a dictionary that maps numerical month values to their corresponding month names.
month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
              7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

# day_dict is a dictionary that maps numerical day of the week values to their corresponding day names.
day_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
            3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}


def get_aggregate_plots(data_frame: pd.DataFrame):

    '''
        Generates aggregate plots for power consumption data over different time intervals.
    '''

    df = data_frame.copy()

    def update_trace(button):
        if button.label == 'Max':
            return [False, True, False]
        elif button.label == 'Min':
            return [False, False, True]
        elif button.label == 'Average':
            return [True, False, False]
        else:
            return [True, True, True]

    plots_json = {}

    for item in time_interval_mapping.items():
        state = item[0].capitalize()
        symbol = item[1]

        duration_avg = df['power'].resample(symbol).mean()
        duration_max = df['power'].resample(symbol).max()
        duration_min = df['power'].resample(symbol).min()

        fig = make_subplots(
            rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02)

        duration_avg_trace = go.Scatter(
            x=duration_avg.index, y=duration_avg.values, mode='lines', name=f'{state} Average Power Consumption')
        duration_max_trace = go.Scatter(x=duration_max.index, y=duration_max.values, mode='markers',
                                        name=f'{state} Max Power Consumption', marker=dict(size=8, color='red'))
        duration_min_trace = go.Scatter(x=duration_min.index, y=duration_min.values, mode='markers',
                                        name=f'{state} Min Power Consumption', marker=dict(size=8, color='green'))

        fig.add_trace(duration_avg_trace, row=1, col=1)
        fig.add_trace(duration_max_trace, row=1, col=1)
        fig.add_trace(duration_min_trace, row=1, col=1)

        buttons = [
            dict(label='Max', method='restyle', args=[
                 {'visible': [False, True, False]}]),
            dict(label='Min', method='restyle', args=[
                 {'visible': [False, False, True]}]),
            dict(label='Average', method='restyle', args=[
                 {'visible': [True, False, False]}]),
            dict(label='All', method='restyle', args=[
                 {'visible': [True, True, True]}])
        ]

        fig.update_xaxes(title_text="Timestamp", row=1, col=1)
        fig.update_yaxes(title_text=f"{state} Power Consumption", row=1, col=1)
        fig.update_layout(showlegend=True, updatemenus=[dict(
            type='buttons', showactive=True, buttons=buttons, x=1.20, y=0.6)], height=600)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        plots_json[state.lower()+"_plot"] = graphJSON

    return plots_json


def get_weekday_plots(data_frame: pd.DataFrame):

    '''
        Generates plots depicting power consumption trends for each day of the week across different months and years.
    '''

    df = data_frame.copy()
    daily = df['power'].resample('D').mean()
    dates = pd.Series(daily.index)
    power_device = pd.DataFrame()
    power_device["day"] = dates.dt.dayofweek
    power_device["month"] = dates.dt.month
    power_device['year'] = dates.dt.year
    power_device['power'] = daily.values
    power_device.day.astype('int')
    power_device.month.astype('int')
    power_device.power.astype('float')
    group_mean = power_device.groupby(['year', 'month', 'day']).power.mean()

    year_dict = Counter()
    for item in group_mean.index:
        year_dict[item[0]] = Counter()
    for year in year_dict.keys():
        for month in range(1, 13):
            year_dict[year][month] = Counter()
    for item in zip(group_mean.index, group_mean.values):
        year_dict[item[0][0]][item[0][1]][item[0][2]] = round(item[1], 2)

    plots_month_wise = Counter()
    for year in year_dict.keys():
        plots_month_wise[year] = Counter()
    for year in year_dict.keys():
        if (len(year_dict[year].keys()) == 0):
            continue
        for i in range(1, 13):
            plotable_dict = year_dict[year][i]
            if len(plotable_dict.keys()) == 0:
                continue

            plotable_dict = {
                'day_name': [day_dict[x] for x in range(0, 7)],
                'power': [0 if x not in plotable_dict else plotable_dict[x] for x in range(0, 7)]
            }

            printer_daywise_df = pd.DataFrame(plotable_dict)
            fig = px.bar(
                printer_daywise_df,
                x='day_name',
                y='power',
                text='power',
                title=f'{month_dict[i]}, {year}',
            )

            fig.update_xaxes(title_text='Day Of Weeks')
            fig.update_yaxes(title_text='Power (W)')
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            plots_month_wise[year][month_dict[i]] = graphJSON
    plot_json = {"weekday_plot": plots_month_wise}
    return plot_json


def get_plots(data_frame: pd.DataFrame):

    '''
        Generates various types of plots based on power consumption data.
    '''

    df = data_frame.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    plots_json = {}
    weekday_plots_json = get_weekday_plots(df)
    aggregate_plots_json = get_aggregate_plots(df)
    plots_json.update(aggregate_plots_json)
    plots_json.update(weekday_plots_json)
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
