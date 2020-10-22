import os, json, datetime, dateutil
import dotenv

import numpy as np
import pandas as pd
import sqlalchemy as sa

import plotly.graph_objects as go
import plotly.offline as pyo

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

dotenv.load_dotenv(r"D:\personal\creds\creds.env")

uid = os.getenv("uid_pgsql")
pw = os.getenv("pwd_pgsql")
host = "localhost"
port = 5432
db = "twitscrape"
db_url = f"postgresql+psycopg2://{uid}:{pw}@{host}:{port}/{db}?gssencmode=disable"
        
engine = sa.create_engine(db_url)

with open("query.sql", "r") as f:
    stmt = f.read()

with engine.connect() as conn:
    df = pd.concat(objs=[chunk for chunk in pd.read_sql(sa.text(stmt), conn, chunksize=3000)], ignore_index=True, sort=False)

df.set_index("datetime", inplace=True)
df.sort_index(inplace=True)
df["dt_hour"] = df.index.floor("h")
df["hashtag"] = df["hashtag"].str.lower()

app = dash.Dash()

# Elements
elem_dummy = html.H3(
    children=""
)

elem_tweet_counter = html.H2(
    id="tweet-count",
    style={
        "display": "inline-block",
        "float": "left",
        "width": "48%",
        "text-align": "center"
    }
)

elem_user_counter = html.H2(
    id="user-count",
    style={
        "display": "inline-block",
        "float": "right",
        "width": "48%",
        "text-align": "center"
    }
)

elem_datefilt_header = html.H3(
    children="Date filter"
)

elem_geofilt_header = html.H3(
    children="Country filter"
)

elem_button = html.Button(
    id="filter-button", 
    n_clicks=0,
    children="Apply"
)

# Plots

plot_trend = dcc.Graph(
    id="plot-trend"
)

plot_geo = dcc.Graph(
    id="plot-geo"
)

plot_pie = dcc.Graph(
    id="plot-pie"
)

plot_bar_hashtags = dcc.Graph(
    id="plot-bar-hashtags"
)

plot_bar_users = dcc.Graph(
    id="plot-bar-users"
)

plot_bar_recipients = dcc.Graph(
    id="plot-bar-recipients"
)

# Filters

filt_daterange = dcc.DatePickerRange(
    id="filter-daterange",
    min_date_allowed=df.index.date.min(),
    max_date_allowed=df.index.date.max(),
    initial_visible_month=df.index.date.min(),
    start_date=df.index.date.min(),
    end_date=df.index.date.min() + dateutil.relativedelta.relativedelta(days=1)
)

filt_country = dcc.Dropdown(
    id="filter-dropdown",
    options=[{"label": "All", "value": "All"}] + [{"label": c, "value": c} for c in df[df["country"].notnull()]["country"].sort_values().unique()],
    value="All",
    multi=True
)


app.layout = html.Div(
    [
        # Title
        html.Div(
            [
                html.H1(
                    className="app-title",
                    id="app-title",
                    children="New Year's 2020 Dashboard"
                )
            ]
        ),
        # Filters
        html.Div(
            className="filter-row",
            children=[
                html.Div(
                    [
                        elem_datefilt_header,
                        filt_daterange
                    ],
                    style={
                        "width": "40%",
                        "display": "inline-block",
                        "text-align": "center",
                        "float": "left"
                    }
                ),
                html.Div(
                    [
                        elem_geofilt_header,
                        filt_country                        
                    ],
                    style={
                        "width": "20%",
                        "display": "inline-block",
                        "text-align": "center"
                    }
                ),
                html.Div(
                    [
                        elem_button
                    ],
                    style={
                        "margin-top": 60,
                        "width": "25%",
                        "display": "inline-block",
                        "float": "right"
                    }
                )
            ]
        ),
        html.Div(
            [
                elem_tweet_counter,
                elem_user_counter
            ]
        ),
        html.Div(
            [
                html.Div(
                    plot_trend,
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "float": "left"
                    }
                ),
                html.Div(
                    plot_geo,
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "float": "right"
                    }
                )
            ]
        ),
        html.Div(
            [
                html.Div(
                    plot_pie,
                    style={
                        "width": "40%",
                        "display": "inline-block",
                        "float": "left"
                    }
                ),
                html.Div(
                    className="filter-row",
                    children=[
                        html.Div(
                            plot_bar_hashtags,
                            style={
                                "width": "33%",
                                "display": "inline-block",
                                "float": "left"
                            }
                        ),
                        html.Div(
                            plot_bar_users,
                            style={
                                "width": "33%",
                                "display": "inline-block",
                            }
                        ),
                        html.Div(
                            plot_bar_recipients,
                            style={
                                "width": "33%",
                                "display": "inline-block",
                                "float": "right"
                            }
                        )
                    ],
                    style={
                        "width": "60%",
                        "display": "inline-block",
                        "float": "left"
                    }
                )
            ]
        )
    ]
)

@app.callback(
    Output("tweet-count", "children"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_tweetcnt(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        cnt = df.loc[start_date:end_date]['id_tweet'].nunique()
    else:
        cnt = df[(df["country"].isin(countries))].loc[start_date:end_date]['id_tweet'].nunique()
    tweet_count = f"Number of Tweets: {cnt}"
    return tweet_count

@app.callback(
    Output("user-count", "children"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_usercnt(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        cnt = df.loc[start_date:end_date]['id_user'].nunique()
    else:
        cnt = df[(df["country"].isin(countries))].loc[start_date:end_date]['id_user'].nunique()
    user_count = f"Number of Tweets: {cnt}"

    return user_count

@app.callback(
    Output("plot-trend", "figure"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_trend(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        data = df.loc[
            start_date:end_date
        ].groupby(
            "dt_hour", as_index=True
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique()),
                "id_user": lambda x: len(x.unique())
            }
        )
    else:
        data = df[
            (df["country"].isin(countries))
        ].loc[
            start_date:end_date
        ].groupby(
            "dt_hour", as_index=True
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique()),
                "id_user": lambda x: len(x.unique())
            }
        )

    traces = [
        go.Scatter(
            x=data.index,
            y=data["id_tweet"],
            mode="lines",
            name="Tweets",
            marker={
                "color": "#1da1f2"
            }
        ),
        go.Scatter(
            x=data.index,
            y=data["id_user"],
            mode="lines",
            name="Users",
            marker={
                "color": "#657786"
            }
        )
    ]

    layout = {
        "title": "Tweets over time",
        "xaxis": {"title": "Date and Hour"},
        "yaxis": {"title": "Volume"},
        "hovermode": "closest"
    }

    fig_dict = {"data": traces, "layout": layout}

    return fig_dict

@app.callback(
    Output("plot-geo", "figure"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_geo(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        data = df.loc[
            start_date:end_date
        ][["id_tweet", "latitude", "longitude"]
        ].drop_duplicates(
            subset=["id_tweet"]
        )
    else:
        data = df[
            (df["country"].isin(countries))
        ].loc[
            start_date:end_date
        ][["id_tweet", "latitude", "longitude"]
        ].drop_duplicates(
            subset=["id_tweet"]
        )

    traces = [
        go.Densitymapbox(
            lat=data["latitude"],
            lon=data["longitude"],
            z=df.loc[start_date:end_date]["id_tweet"],
            radius=15,
            colorscale="Blues",
            showscale=False,
            opacity=0.65
        )
    ]

    layout = go.Layout(
        title="Tweets by Location",
        hovermode="closest",
        mapbox_style="stamen-toner", 
        mapbox_center_lon=-15,
        mapbox_center_lat=35
    )

    fig_dict = {"data": traces, "layout": layout}

    return fig_dict

@app.callback(
    Output("plot-pie", "figure"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_pie(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        data = df.loc[
            start_date:end_date
        ].groupby(
            "source",
            as_index=True
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5)
    else:
        data = df[
            (df["country"].isin(countries))
        ].loc[
            start_date:end_date
        ].groupby(
            "source",
            as_index=True
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5)

    traces = [
        go.Pie(
            labels=data.index,
            values=data["id_tweet"],
            textinfo="percent",
            marker={"colors": ["#1da1f2", "#14171a", "#657786", "#aab8c2", "#e1e8ed"]},
            hole=0.5
        )
    ]

    layout = {
        "title": f"Top 5 Sources of Tweets",
        "hovermode": "closest"
    }

    fig_dict = {"data": traces, "layout": layout}

    return fig_dict

@app.callback(
    Output("plot-bar-hashtags", "figure"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_bar_hashtags(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        data = df.loc[
            start_date:end_date
        ].groupby(
            "hashtag",
            as_index=True
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5).sort_values(
            "id_tweet",
            ascending=True
        )
    else:
        data = df[
            (df["country"].isin(countries))
        ].loc[
            start_date:end_date
        ].groupby(
            "hashtag",
            as_index=True
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5).sort_values(
            "id_tweet",
            ascending=True
        )

    traces = [
        go.Bar(
            x=data["id_tweet"],
            y=data.index,
            orientation="h",
            marker={"color": "#1da1f2"},
        )
    ]

    layout = {
        "title": "Top 10 Hashtags",
        "hovermode": "closest"
    }

    fig_dict = {"data": traces, "layout": layout}

    return fig_dict

@app.callback(
    Output("plot-bar-users", "figure"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_bar_users(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        data = df.loc[
            start_date:end_date
        ].groupby(
            ["id_user", "name_user"],
            as_index=False
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5).sort_values(
            "id_tweet",
            ascending=True
        )
    else:
        data = df[
            (df["country"].isin(countries))
        ].loc[
            start_date:end_date
        ].groupby(
            ["id_user", "name_user"],
            as_index=False
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5).sort_values(
            "id_tweet",
            ascending=True
        )

    traces = [
        go.Bar(
            x=data["id_tweet"],
            y=data["name_user"],
            orientation="h",
            marker={"color": "#14171a"},
        )
    ]

    layout = {
        "title": "Top 10 Twitter Users",
        "hovermode": "closest"
    }

    fig_dict = {"data": traces, "layout": layout}

    return fig_dict

@app.callback(
    Output("plot-bar-recipients", "figure"),
    [
        Input("filter-button", "n_clicks")
    ],
    [
        State("filter-daterange", "start_date"),
        State("filter-daterange", "end_date"),
        State("filter-dropdown", "value")
    ]
)
def update_bar_recipients(n_clicks, start_date, end_date, countries):
    if "All" in countries:
        data = df.loc[
            start_date:end_date
        ].groupby(
            ["id_recipient", "name_recipient"],
            as_index=False
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5).sort_values(
            "id_tweet",
            ascending=True
        )
    else:
        data = df[
            (df["country"].isin(countries))
        ].loc[
            start_date:end_date
        ].groupby(
            ["id_recipient", "name_recipient"],
            as_index=False
        ).agg(
            {
                "id_tweet": lambda x: len(x.unique())
            }
        ).sort_values(
            "id_tweet",
            ascending=False
        ).head(5).sort_values(
            "id_tweet",
            ascending=True
        )

    traces = [
        go.Bar(
            x=data["id_tweet"],
            y=data["name_recipient"],
            orientation="h",
            marker={"color": "#657786"},
        )
    ]

    layout = {
        "title": "Top 10 Tweet Recipients",
        "hovermode": "closest"
    }

    fig_dict = {"data": traces, "layout": layout}

    return fig_dict

if __name__ == '__main__':
    app.run_server()
