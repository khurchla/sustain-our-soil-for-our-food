# run through a standalone test with Dash for a web app
# run this app with 'python app.py' and
# visit http://127.0.0.1:8050/ in your web browser.

# ---------------------------------------------------------------------------------------- 
# imports (boilerplate)
# import config.py file containing my api requirement
import config
# access mapbox api requirement
mapbox_token = config.access_token

# import the required packages using their usual aliases
import dash
import dash_core_components as dcc
import dash_html_components as html
# return when online to uncomment/to run: conda install -n envsoil dash_bootstrap_components 
# import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.graph_objects as go # or plotly.express as px
import pandas as pd

# create (instantiate) the app,
# using the Bootstrap Flatly theme to align with my llc website in development
# return when online to uncomment/to run: conda install -n envsoil dash_bootstrap_components 
app = dash.Dash(__name__) #, external_stylesheets=[dbc.themes.FLATLY])

# -- read the food trade matrix data into pandas from CSV file of 2019 export quantities (exported from analysis in Jupyter Notebook)
dffood = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/dftrade_mx_xq2019ISO3.csv')

# -- read the 4.5 depth soil organic carbon density (%) measurements to filter for selected food's trade export Reporter Countries (exported from analysis in Jupyter Notebook)
dfsoil = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/gdf2flatsurface.csv')

# for a test limit the datapoints to first 50 records
dffood = dffood.head(50)

# ----------------------------------------------------------------------------------------
# create the app's layout (a list of HTML and/or interactive components)
app.layout = html.Div(children=[
    html.H1(id='h1_text_heading', 
        children='Sustain our Soil for our Food', style={'text-align': 'center'}
    ),    
    html.H3(id='h3_text_select_country', 
        children='To begin, select a country where you generally eat.', style={'text-align': 'left'}
    ),
    html.H3(id='h3_text_select_food', 
        children='Then, select a food you frequently eat.', style={'text-align': 'left'}
    ),
    html.P(id='p_text_explanatory_intro', 
        children='Explore how much of the soil is made up of organic carbon where your favorite foods come from. Measurements are a density of organic carbon as a percentage of what makes up the soil at each location from the ground surface down to 4.5 centimeters deep.', 
    style={'text-align': 'left'}
    ),
    html.Div([
    # add a dropdown for audience member using app to select country where they generally eat
    dcc.Dropdown(id='country_dropdown', 
                 options=[{'label': country, 'value': country}
                          for country in dffood['Partner Countries'].unique()]),
    html.Br(),
    html.Div(id='country_output'),
    html.Div([
    # add a dropdown for audience member using app to select a food they frequently eat
    dcc.Dropdown(id='food_dropdown', 
                 options=[{'label': food, 'value': food}
                          for food in df['Item'].unique()]),
    html.Br(),
    html.Div(id='food_output')

    # dcc.Graph(
    #     id='map-socd',
    #     figure=fig
    # )
])


map_surface = go.Scattermapbox(
    name = 'SOCD Surface Depth',
    lon = df['lon'],
    lat = df['lat'],
    mode = 'markers',
    marker = go.scattermapbox.Marker(
        size = df['SOCD'],
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
# fig.add_trace( ... )

# fig.update_layout(...)

fig.show()

# ----------------------------------------------------------------------------------------
# callback functions

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