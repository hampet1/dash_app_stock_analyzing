import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import math

# style defined using python dictionary syntax
from assets.styles import SIDEBAR,TOPBAR,CONTENT,CONTENT_TOP


# importing function for importing and calculation data
from functions.funtions import get_data, calculate_log_return, top_ten_active_stocks, mean_of_log_return, risk_of_return

# import stats models for forecasting
from models.models import arma_model

# initialize dash
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

# first create side bar and main page

sidebar = dbc.FormGroup(
    [
        html.H6('10 most active stocks today',
               style={ 'textAlign': 'center'}),
        dcc.Dropdown(
            id='dropdown',
            # pick one of the top ten active stock
            options= top_ten_active_stocks(),
            multi=False,
        ),
        html.Br(),
        html.H6("Look up an arbitrary stock ticker", style={ 'textAlign': 'center'}),
        html.Div([
                dcc.Input(id='stock_ticker', type='text', placeholder="e.g. MSFT", style={'margin-left': '25%','width':'50%'})
        ]),
        html.Br(),
        html.P("how many stocks to buy?", style={ 'textAlign': 'center'}),
        dcc.Input(id="input1", type="number", style={'margin-left': '25%','width':'50%'}),
        html.Br(),
        html.Br(),
        html.P("avg return and volatility last X days", style={ 'textAlign': 'center'}),
        dcc.Input(id="input2", type="number", placeholder="e.g. 5",style={'margin-left': '25%','width':'50%'}),
        html.Br(),
        html.P(id='result',style={'color': 'blue', 'fontSize': 18, 'textAlign':'center'}),
        html.Hr(),
        html.P('choose prediction model', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.RadioItems(
            id='radio_button',
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
            style={'textAlign':'center'}

        )]),
        html.Br(),
        html.Hr(),
        html.H6("forecast up to 7 days ahead stock price", style={
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
                html.P(['Choose of one the 10 most active stocks or make your own choices e.g. check out ', dcc.Link('yahoo finance', href='https://finance.yahoo.com/')]),
            ],
    style=TOPBAR,
)



# the whole layout
app.layout = html.Div([
    nav,
    sidebar,
    content_second_row,
    content_third_row,
    content_forth_row
])





@app.callback(
    Output('result', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('input1', 'value'),
     State('stock_ticker','value'),
     ])

def total(n_clicks, dropdown_value, input1, stock_ticker):
    """
     choosing last value (todays value) and only price
     using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is not None and input1 is not None:
        value = dropdown_value
        df = get_data(value)
        price = round(df.iloc[-1], 2)
        return "total cost is: $", (price * input1)
    if stock_ticker is not None and input1 is not None:
        value = stock_ticker
        df = get_data(value)
        price = round(df.iloc[-1], 2)
        return "total cost is: $", (price * input1)
    if input1 is None and (dropdown_value is None or stock_ticker is None):
        raise PreventUpdate




@app.callback(
    Output('dropdown','value'),
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('stock_ticker','value')
     ],
    prevent_initial_call=True)


#update our graph
def graph_1(n_clicks, dropdown_value,  stock_ticker):
    """
    print price of a given stock
    using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None and stock_ticker is None:
        raise PreventUpdate
    print("arbitrary tick is: ", stock_ticker)

    if dropdown_value is not None and stock_ticker is not None:
        title = str(dropdown_value)
        print("title is", title)
        value = dropdown_value
        print("value is:", value)

    if dropdown_value is not None:
        title = str(dropdown_value)
        print("title is", title)
        value = dropdown_value
        print("value is:", value)

    if stock_ticker is not None:
        value = stock_ticker
        title = stock_ticker


    df = get_data(value)
    price = round((df.iloc[-1]), 2)
    fig = px.line(df,x=df.index, y="Adj Close",title= f"{title} price, current price (USD) per stock is: {price}", labels = {'x':'Date','y':'Price [USD]'})
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

    return 0, fig




@app.callback(
    Output('graph_2', 'figure'),
    Output('input2','value'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('stock_ticker','value' ),
     State('input2','value')
     ])


#update our graph
def graph_2(n_clicks, dropdown_value,  stock_ticker, input2):
    """
    print price of a given stock
    using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None and stock_ticker is None:
        raise PreventUpdate
    if dropdown_value is not None:
        title = dropdown_value
        value = dropdown_value
        #title = "".join(dropdown_value)
    if stock_ticker is not None:
        value = stock_ticker
        title = stock_ticker
    if input2 is not None:
        days = input2

        # get data accepts a single element
    df= get_data(value)
    log_ret = calculate_log_return(df)
    # mean of return and volatility, we can't enter more days than the total number of records
    if input2 and len(log_ret) >= days:
        avg = mean_of_log_return(log_ret[-days:])
        # volatility (std) of return last 30 days
        vol = risk_of_return(log_ret[-days:])
        text = f"{title} log daily return [%], average return and volatility over last {days} days: {avg}% [return], {vol}% [volatility]"
    else:
        text = f"{title} log daily return [%]"
    # just copying indexes(dates) to create another column with date

    fig = px.line(log_ret,x=log_ret.index, y="Adj Close", title= text,
                  labels = {'x':'Date','y':'log rate of return [%]'})
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
    [Input('submit_button', 'n_clicks'),
     State('dropdown', 'value'),
     State('radio_button', 'value'),
     State('forecast', 'value')
     ])

# graph 3
def graph_3(n_clicks, dropdown_value, radio_button, forecast):
    """
    print log rate of return
    using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None:
        raise PreventUpdate
    if radio_button == None:
        raise PreventUpdate
    if forecast == 0:
        raise PreventUpdate
    else:
        #graph_3.style = 'block'
        # dropdown value is a list of values
        #title = "".join(dropdown_value)
        value = dropdown_value
        # check out the value
        type_of_model = str(radio_button)
        # get data accepts a single element
        df = get_data(value)
        log_ret = calculate_log_return(df)
        days_forecast = forecast
        log_ret = pd.DataFrame(log_ret, columns=["Adj Close"])
        our_model = arma_model(log_ret,type_of_model,days_forecast)
        last_50 = our_model.tail(50)
        # just copying indexes(dates) to create another column with date
        fig = px.line(last_50,x=last_50.index, y="Adj Close", title= f" forecasting using {type_of_model}",
                      labels = {'x':'Date','y':'log rate of return [%]'})
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

        return fig







if __name__ == '__main__':
    app.run_server(debug=True,port=8085)