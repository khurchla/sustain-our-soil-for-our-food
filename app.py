# run through a standalone test with Dash for a web app
# run this app with 'python app.py' and
# visit http://127.0.0.1:8050/ in your web browser.

# ---------------------------------------------------------------------------------------- 
# prepare environment (boilerplate)
# access mapbox token
mapbox_access_token = open(".mapbox_token").read()

# import the required packages using their usual aliases
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go # or plotly.express as px
import pandas as pd

# ----------------------------------------------------------------------------------------
# create (instantiate) the app,
# using the Bootstrap Flatly theme to align with my llc website in development (dadeda.design)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# ----------------------------------------------------------------------------------------
# -- add the data
# -- read the food trade matrix data into pandas from CSV file of 2019 export quantities (exported from analysis in Jupyter Notebook)
# prepared using original dataset FAOSTAT Detailed trade matrix: All Data Normalized from https://fenixservices.fao.org/faostat/static/bulkdownloads/Trade_DetailedTradeMatrix_E_All_Data_(Normalized).zip
# # full dataset
# dffood = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/dftrade_mx_xq2019ISO3.csv')
# smaller test dataset top 2 rows of each group by Item
dffood = pd.read_csv('/Users/kathrynhurchla/Documents/GitHub/sustain-our-soil-for-our-food/data/dftrade_mx_xq2019ISO3_top_n_rows.csv')

# -- read the 4.5 depth soil organic carbon density (%) measurements to filter for selected food's trade export Reporter Countries (exported from analysis in Jupyter Notebook)
# prepared using original dataset Soil organic carbon density: SOCD5min.zip from http://globalchange.bnu.edu.cn/research/soilw
# # full dataset
# dfsoil = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/gdf2flatsurface.csv')
# smaller test dataset
dfsoil = pd.read_csv('/Users/kathrynhurchla/Documents/GitHub/sustain-our-soil-for-our-food/data/gdf2flatsurface_top_n_rows.csv')

# ----------------------------------------------------------------------------------------
# create the app's layout (a list of HTML and/or interactive components)
app.layout = html.Div(children=[
    html.H1('Sustain our Soil for our Food'
    ),    
    html.P('Explore how much of the soil is made up of organic carbon where your favorite foods come from. Measurements are a density of organic carbon as a percentage of what makes up the soil at each location from the ground surface down to 4.5 centimeters deep.', 
    style={'text-align': 'left'}
    ),
    
    # add a dropdown for audience member using app to select country where they generally eat
    # add a brief instructive subheading as a label
    html.Div(children=[
    html.H5('To begin, select a country where you generally eat.'
    ),
    # give more text tips on how to easily find countries
    html.P('Start typing in the box below to filter countries to choose from in the drop down menu.'
    ),
    dcc.Dropdown(id='trade_partner_country_dropdown', 
                 options=[{'label': country, 'value': country}
                          # series values needed to be sorted first before taking unique to prevent errors
                          for country in dffood['Partner Countries'].sort_values().unique()
                 ],
                #  value='United States', # None so no selection is defaulted upon each load of the app page
                 placeholder='Select Country',
                 multi=False, # True to allow multiple Country selections
                 searchable=True, # allows type in search to filter dropdown options that show
                 clearable=True, # shows an 'X' option to clear selection once selection is made
                 persistence=True, # True is required to use a persistence_type
                 persistence_type='session', # remembers dropdown value selection until browser tab is closed (saves after refresh) 
                 style={"width": "50%"}
    ),
    html.Br(),
    ]),
    # add a dropdown for audience member using app to select a food they frequently eat
    html.Div([
    # add a brief instructive subheading as a label
    html.H5('Then, select a food you enjoy.', style={'text-align': 'left'}
    ),
    dcc.Dropdown(id='food_dropdown',
                 options=[], # empty because callbacks are populating this below, based on country selection(s)
                #  options=[{'label': food, 'value': food}
                #           # series values needed to be sorted first before taking unique to prevent errors
                #           for food in dffood['Item'].sort_values().unique()
                #  ],
                 placeholder='Select Food',
                 searchable=True, 
                 clearable=True, # shows an 'X' option to clear selection once selection is made
                 persistence=True, # True is required to use a persistence_type
                 persistence_type='session', # remembers dropdown value selection until browser tab is closed (saves after refresh) 
                 style={"width": "50%"}
    ),
    html.Br(),
    ]),

    html.Div([
        dcc.Graph(
        id='map-socd',
        config={'displayModeBar': False, 'scrollZoom': True}
        )
    ]),
])

# ----------------------------------------------------------------------------------------
# callback decorators and functions
# connecting the Dropdown values to the graph

# populate the options of food dropdown based on countries dropdown selection(s)
@app.callback(
    Output('food_dropdown', 'options'),
    Input('trade_partner_country_dropdown', 'value')
)

def set_food_options(selected_partner_country):
    # using == because selected_partner_country is a string, not a list (with a list use .isin)
    df_sub = dffood[dffood['Partner Countries'] == selected_partner_country]
    return [{'label': s, 'value': s} for s in sorted(df_sub['Item'].unique())]

# populate initial values of food dropdown
@app.callback(
    Output('food_dropdown', 'value'),
    Input('food_dropdown', 'options')
)

def set_food_value(available_options):
    return [x['value'] for x in available_options]

# Output of graph; return the selected options from the dropdown menus and input correlating trade Reporter Country(ies)'s location to the map
@app.callback(
    Output('map-socd', 'figure'),
    [Input('trade_partner_country_dropdown', 'value'),
     State('food_dropdown', 'value')]
)

def update_selected_trade_partner(selected_partner_country, selected_food):
    # always make a copy of any dataframe to use in the function
    # define the subset of data that matches the selected values from both dropdowns
    dfsoil_sub = dfsoil # full dataframe with geo points
    if bool(selected_partner_country): # if no country is selected, this is falsy so no filtering
        if len(selected_food) == 0: # if no food is selected 
            return dash.no_update # dash.no_update prevents any single output updating    
    else:
        # take a subset of food trade data including rows containing Partner Countries matching country dropdown selection, 
        # using == because selected_partner_country is a string, not a list (with a list use .isin); using binary OR '|' instead of AND '&'
        dffood_sub = dffood[(dffood['Partner Countries'] == selected_partner_country) |
                        # including rows with food item traded matching food dropdown selection
                        # using == because selected_food is a string, not a list (with a list use .isin)
                        (dffood['Item'] == selected_food)]
        # loop over the soil data and return only rows with soil country matching the food trade subset Reporter Country
        # first attempt was: return [{'label': r, 'value': r} for r in dfsoil_sub['country_iso_a3'].isin(dffood_sub['Reporter Country ISO3'])]
        # next attempt was: return [{'label': r, 'value': r} for r in dfsoil_sub['Reporter Country ISO3'].reset_index(drop=True) == dffood_sub['Reporter Country ISO3'].reset_index(drop=True)]
        # next attempt was: return [{'label': r, 'value': r} for r in dfsoil_sub['Reporter Country ISO3'].reset_index(drop=True).equals(dffood_sub['Reporter Country ISO3'].reset_index(drop=True))]
        return [{'label': r, 'value': r} for r in dfsoil_sub.loc[dfsoil_sub['country_iso_a3'].isin(dffood_sub['Reporter Country ISO3'])]]

    # create figure variables for the graph object
    locations = [go.Scattermapbox(
                 name = 'SOCD at Surface Depth to 4.5cm',
                 lon = dfsoil_sub['lon'],
                 lat = dfsoil_sub['lat'],
                 mode = 'markers',
                 marker = go.scattermapbox.Marker(
                     size = dfsoil_sub['SOCD'],
                     color = 'fuchsia', # organic matter hex color #a99e54 was not visible on map terrain of similar color
                     opacity = 0.7
                 ),
                 hoverinfo='text',
                 hovertext=str(dfsoil_sub['SOCD']) + '% Organic Carbon Density'
    )]

    # add a mapbox image layer below the data
    layout = go.Layout(
                uirevision='foo', # preserves state of figure/map after callback activated
                clickmode='event+select',
                hovermode='closest',
                hoverdistance=2,
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    style='white-bg'
                ),
                autosize=True,
                mapbox_layers=[
                    {
                        'below': 'traces',
                        'sourcetype': 'raster',
                        'source': [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                ]
    )

    # Return figure
    return {
        'data': locations,
        'layout': layout
    }
    
    # fig = go.Figure(data=data, layout=layout) # or any Plotly Express function e.g. px.bar(...)

# ----------------------------------------------------------------------------------------
# run the app
if __name__ == '__main__':
    app.run_server(debug=True)  # if inside Jupyter Notebook, add use_reloader=False inside parens to turn off reloader