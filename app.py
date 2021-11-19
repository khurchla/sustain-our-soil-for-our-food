# run through a standalone test with Dash for a web app
# run this app with 'python app.py' and
# visit http://127.0.0.1:8050/ in your web browser.

# import config.py file for mapbox access token as config.access_token
import config

mapbox_token = config.access_token

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go # or plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

# read the data from file of 4.5 depth soil organic carbon density (%)
df = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/gdf2flatsurface.csv')

df = df.head(50)

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

app.layout = html.Div(children=[
    html.H1(
        children='Sustain our Soil for our Food'
    ),    

    html.Div(children='Explore how much organic carbon is in the soil where your favorite foods come from.'
    ),

    # dcc.Graph(
    #     id='map-socd',
    #     figure=fig
    # )
])

fig.show()

if __name__ == '__main__':
    app.run_server(debug=True)  # if inside Jupyter Notebook, add use_reloader=False inside parens to turn off reloader