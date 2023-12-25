from typing import List, Tuple
import pandas as pd
import plotly.express as px
import plotly
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from collections import Counter
from scipy.stats import linregress

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
    df.set_index('timestamp', inplace=True)

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
    df.set_index('timestamp', inplace=True)
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


def night_time_zones(df: pd.DataFrame, timestamp_col: str = 'timestamp', start: int = 20, end: int = 6) -> tuple[
    tuple[int, int], ...]:
    """
    Returns a list of tuples containing the integer location of start and end of nighttime zones in the dataframe
    """
    flag = 0  # 0 for start 1 for end
    night_zones: List[Tuple[int, int]] = []  # To store the zones
    start_end = [0, 0]  # Start and end of the zones

    # Iterating through each rows
    for i, time in enumerate(df[timestamp_col].dt.hour.to_numpy()):

        # Set the start of the zone if the time is greater than or equal to start time and flag is not set
        if time >= start and not flag:
            start_end[0] = i  # Set the start of the zone
            flag = 1  # Set the flag to indicate that start is set

        # Set the end of the zone if the time is less than end time and flag is set
        elif time < end and flag:
            start_end[1] = i  # Set the end of the zone
            night_zones.append(tuple(start_end))  # Append the zone to the list
            start_end = [0, 0]  # Reset the start and end
            flag = 0  # Reset the flag

    return tuple(night_zones)


def positive_slope_zones(df: pd.DataFrame, use_col: str, dist_to_check=5, min_slope=1) -> tuple[tuple[int, int], ...]:
    """
    Returns a list of tuples containing the integer location of start and end of positive slope zones in the dataframe
    """
    pos_slope_zone = []  # Value to store the negative slope zone

    start = ...  # Start of the zone

    # Iterating through each rows
    for j in range(len(df.index)):
        indi = j  # Index of the current row

        # Left Value
        if j != 0:
            left = df.iloc[j - 1][use_col]
        else:
            left = df.iloc[j][use_col]

        current = df.iloc[j][use_col]  # Current Value
        # Next value is assigned after next If Statement to avoid the Index Out of Bound Error

        # Consider the end of the zone as maxima or not by comparing it with its previous value
        if j == df.shape[0] - 1:
            if current > left:
                pos_slope_zone.append((start, indi))
            continue

        right = df.iloc[j + 1][use_col]  # Next Value

        # Consider the start of the zone as minima or not by comparing it with its next value
        if j == 0:
            # Compare only with the next value
            if current <= right:
                start = indi
            continue

        # Assign a point as minima if it's lower than both of left and right point
        if current <= left and current < right:
            start = indi
            continue

        # Assign a point as maxima if it's higher than both of left and right point
        if current > left and current >= right:
            pos_slope_zone.append([start, indi])
            continue

    # Merge two pairs which belongs to same slope but seperated due to a flat line or some noise in between
    i = 0  # counter

    # Iterate through each zone
    while i < len(pos_slope_zone) - 1:

        # If the distance between the end of the first zone and the start of the second zone is less than dist_to_check
        # and the value at the end of the first zone is lesser than the value at the start of the second zone
        if (pos_slope_zone[i + 1][0] - pos_slope_zone[i][1] <= dist_to_check and
                df[use_col].iloc[pos_slope_zone[i + 1][0]] >= df[use_col].iloc[pos_slope_zone[i][1]]):
            # Merge the two zones
            pos_slope_zone[i][1] = pos_slope_zone[i + 1][1]
            pos_slope_zone.pop(i + 1)

            # Decrement the counter to check the merged zone with the next zone
            i -= 1

        i += 1

    # Remove zones with slope less than min_slope
    if min_slope:

        # Iterate through each zone
        i = 0  # counter
        while i < len(pos_slope_zone) - 1:

            # Calculate the slope of the zone
            slope = linregress(df.iloc[pos_slope_zone[i][0]:pos_slope_zone[i][1] + 1].index,
                               df[use_col].iloc[pos_slope_zone[i][0]:pos_slope_zone[i][1] + 1])[0]

            # If the slope is less than min_slope, remove the zone
            if slope < min_slope:
                pos_slope_zone.pop(i)

                # Decrement the counter to check the next zone
                i -= 1

            i += 1

    return tuple(pos_slope_zone)

def get_stats(df: pd.DataFrame, use_col: str) -> list[float]:
    """
    Creates a list of different zones with respect to the energy consumption
    """

    stats = df[use_col].describe().to_dict()
    minimum = stats["min"]
    mean = stats["mean"]
    maximum = stats["max"]

    _25 = (mean + minimum)/2
    _50 = mean
    _75 = (mean + maximum)/2

    y_values = [minimum, _25, _50, _75, maximum]

    # return zones, y_values
    return y_values


def get_night_and_slope_highlight_plot(dataframe: pd.DataFrame, time_col: str = 'timestamp', power_col: str = 'power', title='Power (W)',
                     start=20, end=6, dist_to_check=5, min_slope=5) -> str:
    """
    Creates a line plot with night zones and positive slope zones highlighted
    :param df:  The dataframe
    :param time_col: column name of the timestamp column. The column should be of type datetime
    :param power_col: column name of the power column.
    :param title: title of the plot
    :param start:  start time of the night zone
    :param end:  end time of the night zone
    :param dist_to_check:  distance to check for positive slope
    :param min_slope:  minimum slope to consider as positive slope

    :return: the html string of the plot
    """

    df = dataframe.copy()

    # Figure Layout
    layout = go.Layout(
        title=title,
        plot_bgcolor="#FFF",
        hovermode="x",
        hoverdistance=100,  # Distance to show hover label of data point
        spikedistance=1000,  # Distance to show spike# Sets background color to white
        xaxis=dict(
            title="Time",
            linecolor="#BCCCDC",  # Sets color of X-axis line
            showgrid=False,
            showspikes=True,  # Show spike line for X-axis
            # Format spike
            spikethickness=2,
            spikedash="dot",
            spikecolor="#999999",
            spikemode="across",
        ),  # Removes X-axis grid lines
        yaxis=dict(title="Power (W)", linecolor="#BCCCDC"),  # Sets color of Y-axis line
        showlegend=False,
    )

    # Plot the line plot
    fig = go.Figure(go.Scatter(x=df[time_col], y=df[power_col], name=title), layout=layout)

    # Add the night zones
    night_zones = night_time_zones(df, timestamp_col=time_col, start=start, end=end)  # Get the night zones
    for start, end in night_zones:
        fig.add_vrect(x0=df[time_col][start], x1=df[time_col][end], annotation_text="Night", fillcolor='purple',
                      opacity=0.2,
                      annotation_position="top left", annotation=dict(font_size=20, font_family="Times New Roman"))

    # Add the positive slope zones
    zones = positive_slope_zones(df, use_col=power_col, dist_to_check=dist_to_check,
                                                      min_slope=min_slope)  # Get the positive slope zones
    for start, end in zones:
        positive_slope_df = df.iloc[start:end + 1]
        fig.add_trace(go.Scatter(x=positive_slope_df[time_col],
                                 y=positive_slope_df[power_col],
                                 mode='lines',
                                 line=dict(color='red'),
                                 hoverinfo='skip',
                                 showlegend=False))

    # Color the box for the zones
    y_values = get_stats(df, use_col=power_col)
    colors = ['green', 'yellow', 'orange', 'red']
    for i in range(0, 4):
        fig.add_hrect(y0=y_values[i],
                      y1=y_values[i + 1],
                      fillcolor=colors[i],
                      opacity=0.2,
                      layer="below",
                      )
        
    # Return the figure
    plot_json = {}
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    plot_json['night_and_slope_highlighted_plot'] = graphJSON
    return plot_json

