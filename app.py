# run through a standalone test with Dash for a web app
# run this app with 'python app.py' and
# visit http://127.0.0.1:8050/ in your web browser.

# ---------------------------------------------------------------------------------------- 
# prepare environment (boilerplate)
# access mapbox token
token = open(".mapbox_token").read()

# import the required packages using their usual aliases
import dash
from dash import dcc
from dash import html
# return when online to uncomment/to run: conda install -n envsoil dash_bootstrap_components 
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.graph_objects as go # or plotly.express as px
import pandas as pd

# ----------------------------------------------------------------------------------------
# create (instantiate) the app,
# using the Bootstrap Flatly theme to align with my llc website in development (dadeda.design)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# ----------------------------------------------------------------------------------------
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

# for a test limit the datapoints to first 50 records
# dffood = dffood.head(50)

# ----------------------------------------------------------------------------------------
# create variables for the graph objects
map_surface = go.Scattermapbox(
    name = 'SOCD Surface Depth',
    lon = dfsoil['lon'],
    lat = dfsoil['lat'],
    mode = 'markers',
    marker = go.scattermapbox.Marker(
        size = dfsoil['SOCD'],
        color = 'fuchsia', # organic matter hex color #a99e54 was not visible on map terrain of similar color
        opacity = 0.7
    )
)

# add a mapbox image layer below the data
layout = go.Layout(
    mapbox_style='white-bg',
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

data = [map_surface]
fig = go.Figure(data=data, layout=layout) # or any Plotly Express function e.g. px.bar(...)

# ----------------------------------------------------------------------------------------
# create the app's layout (a list of HTML and/or interactive components)
app.layout = html.Div(children=[
    html.H1('Sustain our Soil for our Food'
    ),    
    html.P('Explore how much of the soil is made up of organic carbon where your favorite foods come from. Measurements are a density of organic carbon as a percentage of what makes up the soil at each location from the ground surface down to 4.5 centimeters deep.', 
    style={'text-align': 'left'}
    ),
    html.Div(children=[
    html.H5('To begin, select a country where you generally eat.'
    ),
    html.P('Start typing in the box below to filter countries to choose from in the drop down menu.'
    ),
    # add a dropdown for audience member using app to select country where they generally eat
    dcc.Dropdown(id='country_dropdown', 
                 options=[{'label': country, 'value': country}
                          # series values needed to be sorted first before taking unique to prevent errors
                          for country in dffood['Partner Countries'].sort_values().unique()
                          ],
                 value=None, # None so no selection is defaulted upon each load of the app page
                 placeholder='Select Country',
                 multi=True, # allow multiple Country selections
                 searchable=True, # allows type in search to filter dropdown options that show
                 clearable=True, # shows an 'X' option to clear selection once selection is made
                 persistence=True, # True is required to use a persistence_type
                 persistence_type='session', # remembers dropdown value selection until browser tab is closed (saves after refresh) 
                 style={"width": "50%"}
                 ),
    html.Br(),
    html.Div(id='country_output')
    ]),
    html.Div([
    html.H5('Then, select a food you eat.', style={'text-align': 'left'}
    ),
    # add a dropdown for audience member using app to select a food they frequently eat
    dcc.Dropdown(id='food_dropdown',
                 options=[{'label': food, 'value': food}
                          # series values needed to be sorted first before taking unique to prevent errors
                          for food in dffood['Item'].sort_values().unique()],
                 placeholder='Select Food',
                 searchable=True, 
                 clearable=True, # shows an 'X' option to clear selection once selection is made
                 persistence=True, # True is required to use a persistence_type
                 persistence_type='session', # remembers dropdown value selection until browser tab is closed (saves after refresh) 
                 style={"width": "50%"}
                 ),
    html.Br(),
    html.Div(id='food_output')
    ]),

    dcc.Graph(
        id='map-socd',
        figure=fig
    )
])

# fig.add_trace( ... )

# fig.update_layout(...)

# fig.show()

# ----------------------------------------------------------------------------------------
# callback functions
# connecting the Dropdown values to the graph

# return the selected country from the dropdown menu
@app.callback(Output('country_output', 'children'),
              Input('country_dropdown', 'value'))
# display to the audience their selection for confirmation
def display_selected_country(country):
    if country is None:
        return '' # color = 'Nothing' if not also using this in other callbacks
        return 'You selected ' + country

# return the selected food from the dropdown menu
@app.callback(Output('food_output', 'children'),
              Input('food_dropdown', 'value'))
# display to the audience their selection for confirmation
def display_selected_food(food):
    if food is None:
        return '' # color = 'Nothing' if not also using this in other callbacks
        return 'You selected ' + food        

# ----------------------------------------------------------------------------------------
# run the app
if __name__ == '__main__':
    app.run_server(debug=True)  # if inside Jupyter Notebook, add use_reloader=False inside parens to turn off reloader