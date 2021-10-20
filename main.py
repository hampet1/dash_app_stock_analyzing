import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np

# style defined using python dictionary syntax
from assets.styles import SIDEBAR, TOPBAR, CONTENT, CONTENT_TOP, FOOTER

# functions for manipulation with default stock price
from functions.funtions import get_data, log_return, top_ten_active_stocks, mean_log_return, risk_of_return, log

# import stats models for forecasting
from models.models import arma_model

# initialize dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# first create side bar and main page

sidebar = dbc.FormGroup(
    [
        html.H6('10 most active stocks today',
                style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='dropdown',
            # pick one of the top ten active stock
            options=top_ten_active_stocks(),
        ),
        html.Br(),
        html.H6("Look up an arbitrary stock ticker", style={'textAlign': 'center'}),
        html.Div([
            dbc.Input(id='stock_ticker', type='text', placeholder="e.g. MSFT",
                      style={'margin-left': '25%', 'width': '50%'})
        ]),
        html.Br(),
        html.P("how many stocks to buy?", style={'textAlign': 'center'}),
        dcc.Input(id="num_of_stocks", value=0, type="number", placeholder="e.g. 10",
                  style={'margin-left': '25%', 'width': '50%'}),
        html.Br(),
        html.Br(),
        html.P("avg return and volatility last X days", style={'textAlign': 'center'}),
        dcc.Input(id="ret_and_vol", type="number", value=0, placeholder="e.g. 5",
                  style={'margin-left': '25%', 'width': '50%'}),
        html.Hr(),
        html.P('choose a prediction model', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='type_of_model',
            options=[{
                'label': 'AR',
                'value': 'AR'
            },
                {
                    'label': 'MA',
                    'value': 'MA'
                },
                {
                    'label': 'ARMA',
                    'value': 'ARMA'
                }
            ],
            inline=True,
            style={'textAlign': 'center'}

        )]),
        html.Br(),
        html.Hr(),
        html.P("forecast up to 7 days ahead stock price", style={
            'textAlign': 'center'}),
        dbc.Card([dcc.Slider(
            id='forecast',
            min=0,
            max=7,
            step=1,
            value=0,
            marks={
                0: '0',
                1: '1',
                2: '2',
                3: '3',
                4: '4',
                5: '5',
                6: '6',
                7: '7'
            },
        ),
            html.Div(id='slider_output_container')
        ]),
        html.Br(),
        html.Br(),
        dbc.Button(
            # it's component for state
            id='submit_button',
            # n_clicks - component property
            n_clicks=0,
            children='Submit',
            color='primary',
            block=True
        ),
    ],
    style=SIDEBAR,
)

# main content graphs

content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=12,
        )
    ],
    style=CONTENT_TOP,
)

content_third_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_2'), md=12,
        )
    ],
    style=CONTENT,
)

content_forth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_3'), md=12,
        )
    ],
    style=CONTENT,
)

nav = html.Div(
    [
        html.H4("stock prices & stock predictions"),
        html.Br(),
        html.P(['Choose of one the 10 most active stocks or make your own choices e.g. check out ',
                dcc.Link('yahoo finance', href='https://finance.yahoo.com/', refresh=True)]),
    ],
    style=TOPBAR,
)

footer = html.Footer([
    html.Div([
        html.P("Created by Petr Hamrozi. Disclaimer: Forecasting is for illustrative purposes only and it is not "
               "intended to serve as investment advice")
    ],
        style=FOOTER,
    )
])

# the whole layout
app.layout = html.Div([
    nav,
    sidebar,
    content_second_row,
    content_third_row,
    content_forth_row,
    footer
])




@app.callback(
    Output('graph_1', 'figure'),
    Output('num_of_stocks', 'value'),
    Output('dropdown', 'value'),
    Output('stock_ticker', 'value'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('stock_ticker', 'value'),
     State('num_of_stocks', 'value')
     ])
# update our graph
def graph_1(n_clicks, dropdown_value, stock_ticker, num_of_stocks):
    """
    print price of a given stock and a graph of the price history
    """

    if dropdown_value:
        value = dropdown_value
        title = dropdown_value
    elif stock_ticker:
        value = stock_ticker
        title = stock_ticker
    else:
        raise PreventUpdate

    df = get_data(value)
    price = round((df.iloc[-1]), 2)
    if num_of_stocks:
        total = round(price*int(num_of_stocks), 2)
        text = f"{title.upper()}, current price (USD) per stock is: {price}, total price for {int(num_of_stocks)} stocks is {total}"
    else:
        text = f"{title.upper()}, current price (USD) per stock is: {price}"
    fig = px.line(df, x=df.index, y="Adj_Close", title=text,
                  labels=dict(x="Date", Adj_Close="Price [USD]"))
    fig.update_layout(title_x=0.5)
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    return fig, 0, '', ''


@app.callback(
    Output('graph_2', 'figure'),
    Output('ret_and_vol', 'value'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('stock_ticker', 'value'),
     State('ret_and_vol', 'value')
     ])
# update our graph
def graph_2(n_clicks, dropdown_value, stock_ticker, ret_and_vol):
    """
    print price of a given stock
    alternatively include average return and average volatility over a particular time period
    """
    if dropdown_value:
        value = dropdown_value
        title = dropdown_value
    elif stock_ticker:
        value = stock_ticker
        title = stock_ticker
    else:
        raise PreventUpdate

    if ret_and_vol is not None:
        days = ret_and_vol

    df = get_data(value)
    log_ret = log_return(df)
    # mean of return and volatility, we can't enter more days than the total number of records
    if ret_and_vol and len(log_ret) >= days:
        avg = mean_log_return(log_ret[-days:])
        # volatility (std) of return
        vol = risk_of_return(log_ret[-days:])
        text = f"{title.upper()} log daily return [%], average return and volatility over last {days} days: {avg}% [return], {vol}% [volatility] "
    else:
        text = f"{title.upper()} log daily return [%]"
    fig = px.line(log_ret, x=log_ret.index, y="Adj_Close", title=text,
                  labels=dict(x="Date", Adj_Close="log rate of return [%]"))
    fig.update_layout(title_x=0.5)
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    return fig, 0


@app.callback(
    Output('graph_3', 'figure'),
    Output('forecast', 'value'),
    Output('type_of_model', 'value'),
    [Input('submit_button', 'n_clicks'),
     State('dropdown', 'value'),
     State('stock_ticker', 'value'),
     State('type_of_model', 'value'),
     State('forecast', 'value')
     ])
# graph 3
def graph_3(n_clicks, dropdown_value, stock_ticker, type_of_model, forecast):
    """
    print price history over last 50 days and additional forecasting model: AR or MA or ARMA AR an MA
    order parameters (in a sense of the number of previous lags included in our model) in our model is by default set
    to 2 with respect to a particular model, in order to avoid any errors and increase the evaluation speed of our model
    as the model is used only for illustrative purposes in the first place.

    """
    if dropdown_value:
        value = dropdown_value
        title = dropdown_value
    elif stock_ticker:
        value = stock_ticker
        title = stock_ticker
    else:
        raise PreventUpdate

    if type_of_model is None:
        raise PreventUpdate
    if forecast == 0:
        raise PreventUpdate
    else:

        type_of_model = str(type_of_model)
        df = get_data(value)
        # only log data - it's not return cause the model has set up integrated order = 1, so it substitutes pct_change()
        log_data = log(df)
        days_forecast = forecast
        print("log ret is", log_data)
        log_ret = pd.DataFrame(log_data, columns=["Adj_Close"])
        print("lor ret with a column:", log_ret)
        our_model = arma_model(log_ret, type_of_model, days_forecast)
        # undo log transform
        our_model = np.exp(our_model)
        last_30 = our_model.tail(30)
        last_x = our_model.tail(forecast)
        # just copying indexes(dates) to create another column with date
        fig = px.line(last_30, x=last_30.index, y="Adj_Close", title=f" {title.upper()} forecasting for {forecast} business days, using {type_of_model} model",
                      labels=dict(index="Date", Adj_Close="Price [USD]"))
        # Only thing I figured is - I could do this
        fig.add_scatter(x=last_x.index, y=last_x['Adj_Close'], showlegend=False)
        fig.update_layout(title_x=0.5)
        # Add range slider
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=7,
                             label="1w",
                             step="day",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )

        return fig, 0, ''


if __name__ == '__main__':
    app.run_server(debug=True, port=8085)
