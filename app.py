import plotly_express as px
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

df = pd.read_csv("is24_flat.csv", low_memory=False).fillna(0)
col_options = [dict(label=x, value=x) for x in df.columns]
type_option = [dict(label=x, value=x) for x in df['type_transferType'].unique()]
type_estate = [dict(label=x, value=x) for x in df['type_estateType'].unique()]
marginal_option = [dict(label=x, value=x) for x in ['violin', 'box', 'histogram', 'rug']]
type_state = [dict(label=x, value=x) for x in df['localization_address_state'].unique()]
price_slider_options = [max(1, df['priceInformation_primaryPrice'].min()), df['priceInformation_primaryPrice'].max()]
area_slider_options =  [max(1,df['area_areaRangeFrom'].min()), df['area_areaRangeFrom'].max()]

dimensions = ["x", "y", "color", "facet_col", "facet_row", "type_transfer", "xaxis_type", "yaxis_type", 
              "filter_estate", "filter_state", "price_slider", "area_slider", "marginal_y", "marginal_x"]


body = html.Div(
    [
                html.Div(
            [
                html.Div(
                    [
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Immobilien Objekt Explorer",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "DataScrape from immoscout24.at", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        
                    ],
                    className="one-third column",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div([
            html.P(["x" + ":", dcc.Dropdown(id="x", options=col_options, value="area_areaRangeFrom")]),
            
            html.P(["xaxis_type" + ":", dcc.RadioItems(id='xaxis_type',options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                                                       value='Linear', labelStyle={'display': 'inline-block'})]),
            
            ],
            style={'width': '48%', 'display': 'inline-block'}
            ),
        html.Div([
                html.P(["y" + ":", dcc.Dropdown(id="y", options=col_options, value="priceInformation_primaryPrice")]),
                html.P(["yaxis_type" + ":", dcc.RadioItems(id='yaxis_type',options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                                                       value='Linear', labelStyle={'display': 'inline-block'})]),
                ],
                style={'width': '48%', 'float':'reight', 'display': 'inline-block'}
            ),
        html.Div(
            [
                
                html.P(["marginal_x" + ":", dcc.Dropdown(id="marginal_x", options=marginal_option)]),
                html.P(["marginal_y" + ":", dcc.Dropdown(id="marginal_y", options=marginal_option)]),
                html.P(["color" + ":", dcc.Dropdown(id="color", options=col_options)]),
                html.P(["facet_col" + ":", dcc.Dropdown(id="facet_col", options=col_options)]),
                html.P(["facet_row" + ":", dcc.Dropdown(id="facet_row", options=col_options)]),
                html.P(["type_transfer" + ":", dcc.Dropdown(id="type_transfer", options=type_option, multi=True)]),
                html.P(["filter_estate" + ":", dcc.Dropdown(id="filter_estate", options=type_estate, multi=True)]),
                html.P(["filter_state" + ":", dcc.Dropdown(id="filter_state", options=type_state, multi=True)]),

                html.Div([
                    html.P(["price_slider" + ":", dcc.RangeSlider(id='price_slider', min=price_slider_options[0], max=price_slider_options[1], 
                                                               step=10, value=[price_slider_options[0], price_slider_options[1]])]),
                    html.Div(id='output_price_slider'),
                    ]),
                html.Div([
                    html.P(["area_slider" + ":", dcc.RangeSlider(id='area_slider', min=area_slider_options[0], max=area_slider_options[1], 
                                                               step=10, value=[area_slider_options[0], area_slider_options[1]])]),
                    html.Div(id='output_area_slider'),
                          
                    ]),
            ],
			className="pretty_container",
            style={"width": "25%", "float": "left"},
        ),
		
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
    ], 
)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([body], className="container-float")


def generate_inputs():
    result =  [Input(d, "value") for d in dimensions]
    #result.append(Input('output_price_slider', "))
    return result

def generate_outputs():
     return [
        Output("graph", "figure"),
        Output('output_price_slider', 'children'),
        Output('output_area_slider', 'children'),
    ]


@app.callback(generate_outputs(), generate_inputs())
def make_figure(x, y, color, facet_col, facet_row, type_transfer, xaxis_type, yaxis_type, filter_estate, filter_state, price_slider, area_slider, marginal_y, marginal_x):
    # filter transfer type - Buy, Rent
    filtered_df = df
    if type_transfer:
        filtered_df = filtered_df[filtered_df['type_transferType'].isin(type_transfer)]
    
    # filter estate type - Apartment, Office, House
    if filter_estate:
        filtered_df = filtered_df[filtered_df['type_estateType'].isin(filter_estate)]

    # filter state - Bundesland
    if filter_state:
        filtered_df = filtered_df[filtered_df['localization_address_state'].isin(filter_state)]

    if price_slider:
        filtered_df = filtered_df[(filtered_df['priceInformation_primaryPrice'] >= price_slider[0]) & (filtered_df['priceInformation_primaryPrice'] <= price_slider[1])]

    if area_slider:
        filtered_df = filtered_df[(filtered_df['area_areaRangeFrom'] >= area_slider[0]) & (filtered_df['area_areaRangeFrom'] <= area_slider[1])]

    # Log Axis
    if xaxis_type =="Linear":
        log_x = False
    else:
        log_x = True

    if yaxis_type=="Linear":
        log_y = False
    else:
        log_y = True  

    output_price = 'Price from {} to {}'.format(price_slider[0], price_slider[1])
    output_area =  'Area from {} to {}'.format(area_slider[0], area_slider[1])

    chart1 = px.scatter(
        filtered_df,
        x=x,
        y=y,
        color=color,
        facet_col=facet_col,
        facet_row=facet_row,
		log_x=log_x,
		log_y=log_y,
        marginal_y=marginal_y,
        marginal_x=marginal_x,
        height=700,
    )
    result = [chart1, output_price, output_area]    
    return result


app.run_server(debug=True)
