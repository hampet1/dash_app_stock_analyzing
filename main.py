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
from functions.funtions import get_data

# initialize dash
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])


# first create side bar and main page

sidebar = dbc.FormGroup(
    [
        html.P('Stock tickers',
               style={ 'textAlign': 'center'}),
        dcc.Dropdown(
            id='dropdown',
            options=[{
                'label': 'TESLA',
                'value': 'TSLA'
            }, {
                'label': 'MICROSOFT',
                'value': 'MSFT'
            },
                {
                'label': 'GOOGLE',
                'value': 'GOOGL'
                }
            ],
            value=['TSLA'],  # default value
            multi=False
        ),
        html.Br(),
        html.P('Range Slider', style={
                'textAlign': 'center'
            }),
        dcc.RangeSlider(
            id='range_slider',
            min=0,
            max=20,
            step=0.5,
            value=[5, 15]
        ),
        html.P('Type of prediction', style={
            'textAlign': 'center'
        }),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[{
                'label': 'Daily return',
                'value': 'daily_return'
            },
                {
                    'label': 'Value Two',
                    'value': 'value2'
                },
                {
                    'label': 'Value Three',
                    'value': 'value3'
                }
            ],
            value=[''],
            inline=True
        )]),
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
                html.P(['Choose of the 5 most active stocks or make your own choices on ', dcc.Link('yahoo finance', href='https://finance.yahoo.com/')]),
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
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('dropdown', 'value'),
     State('range_slider', 'value'),
     State('check_list', 'value')
     ])


#update our graph
def graph_1(n_clicks, dropdown_value, range_slider_value, check_list_value):
    """
    print price of a given stock
    """
    # dropdown value is a list of values
    title = "".join(dropdown_value)
    value = dropdown_value
    # get data accepts a single element
    df = get_data(value)
    fig = px.line(df,x="Date", y="Adj Close",title= f"{title} price since X", labels = {'x':'Date','y':'Price [USD]'})
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