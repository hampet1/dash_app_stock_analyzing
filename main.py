import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

# style defined using python dictionary syntax
from assets.styles import SIDEBAR,TOPBAR,CONTENT

# importing function for importing and calculation data
from functions.funtions import get_data, calculate_log_return, top_ten_active_stocks

# import stats models for forecasting
from models.models import arma_model

# initialize dash
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])


# first create side bar and main page

sidebar = dbc.FormGroup(
    [
        html.P('most active stocks',
               style={ 'textAlign': 'center'}),
        dcc.Dropdown(
            id='dropdown',
            # pick one of the top ten active stock
            options= top_ten_active_stocks(),
            multi=False
        ),
        html.Br(),
        html.Div([
            html.Div('current price (USD) per stock is:', style={'color': 'blue', 'fontSize': 15}),
            html.P(id='result',style={'color': 'black', 'fontSize': 18})
        ], style={'textAlign':'center'}),
        html.Br(),
        html.P("how many stocks would you like to buy?"),
        dcc.Input(id="input1", type="number", style={'margin-left': '25%','width':'50%'}),
        html.Br(),
        html.P(id='result2',style={'color': 'black', 'fontSize': 18, 'textAlign':'center'}),
        html.Br(),
        html.P("calculate return of investment(ROI) and risk (we would like to optimize return and risk of investment)choose type of prediction and period"),
        html.Hr(),
        html.P('choose prediction model', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[{
                'label': 'AR',
                'value': 'daily_return'
                },
                {
                    'label': 'MA',
                    'value': 'value2'
                },
                {
                    'label': 'ARMA',
                    'value': 'value3'
                }
            ],
            value=[''],
            inline=True
        )]),
        html.Br(),
        html.Hr(),
        html.H6("forecast up to 7 days ahead stock price", style={
            'textAlign': 'center'}),
        dbc.Card([dcc.Slider(
            id='my_slider',
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
    style=CONTENT,
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
                html.P(['Choose of one the 10 most active stocks or make your own choices on ', dcc.Link('yahoo finance', href='https://finance.yahoo.com/')]),
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
    [State('dropdown', 'value')
     ])

def current_price(n_clicks, dropdown_value):
    """
     choosing last value (todays value) and only price
     using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None:
        raise PreventUpdate
    else:
        value = dropdown_value
        print(dropdown_value)
        # get data accepts a single element
        df = get_data(value)
        print("data for price ", df)
        price = round((df.iloc[-1]),2)
        return price


@app.callback(
    Output('result2', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('input1', 'value')
     ])

def total(n_clicks, dropdown_value, input1):
    """
     choosing last value (todays value) and only price
     using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None or input1 is None:
        raise PreventUpdate
    else:
        value = dropdown_value
        print(dropdown_value)
        # get data accepts a single element
        df = get_data(value)
        print("data for price ", df)
        price = round((df.iloc[-1]),2)
        return "total cost is: ",(price * input1)


@app.callback(
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('check_list', 'value')
     ])


#update our graph
def graph_1(n_clicks, dropdown_value,  check_list_value):
    """
    print price of a given stock
    using error handling to avoid error associated with None value is dropdown value parameter
    """

    if dropdown_value is None:
        raise PreventUpdate
    else:
        # dropdown value is a list of values
        title = "".join(dropdown_value)
        value = dropdown_value
        # get data accepts a single element
        df = get_data(value)
        fig = px.line(df,x=df.index, y="Adj Close",title= f"{title} price since X", labels = {'x':'Date','y':'Price [USD]'})
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

        return fig




@app.callback(
    Output('graph_2', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('check_list', 'value')
     ])

def graph_2(n_clicks, dropdown_value, check_list_value):
    """
    print log rate of return
    using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None:
        raise PreventUpdate
    else:
        title = "".join(dropdown_value)
        value = dropdown_value
        # get data accepts a single element
        df= get_data(value)
        log_ret = calculate_log_return(df)
        # just copying indexes(dates) to create another column with date
        fig = px.line(log_ret,x=log_ret.index, y="Adj Close", title= f"{title} log daily return",
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

        return fig

@app.callback(
    Output('graph_3', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('check_list', 'value')
     ])

# graph 3
def graph_3(n_clicks, dropdown_value, check_list_value):
    """
    print log rate of return
    using error handling to avoid error associated with None value is dropdown value parameter
    """
    if dropdown_value is None:
        raise PreventUpdate
    else:
        title = "".join(dropdown_value)
        value = dropdown_value
        # get data accepts a single element
        df= get_data(value)
        log_ret = calculate_log_return(df)
        # just copying indexes(dates) to create another column with date
        fig = px.line(log_ret,x=log_ret.index, y="Adj Close", title= f"{title} ARIMA return forecasting",
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

        return fig




if __name__ == '__main__':
    app.run_server(debug=True,port=8085)