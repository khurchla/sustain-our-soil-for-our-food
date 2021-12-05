# ---------------------------------------------------------------------------------------- 
# prepare environment (boilerplate)

# import the required packages using their usual aliases
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go # or plotly.express as px
import plotly.express as px
import pandas as pd

# read token string with your access mapbox token from a hidden file 
# saved in environment's root directory same as where this app.py file is
# if you're using GitHub make sure to add '*.mapbox_token' to your .gitignore file
# to prevent your private credentials from being publicly viewed or uploaded to GitHub
mapbox_access_token = open(".mapbox_token").read()

# ----------------------------------------------------------------------------------------
# -- call the data
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
# create (instantiate) the app,
# using the Bootstrap Flatly (light) theme or Darkly (its dark counterpart) to align with my llc website in development (dadeda.design)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH],
                meta_tags=[{'name': 'viewport',
                            # initial-scale is the initial zoom on each device on load
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]
                )

# ----------------------------------------------------------------------------------------
# named variables for the app's layout
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About us", href="#")), #"http://kathrynhurchla.com/", target="_blank"),
        dbc.NavItem(dbc.NavLink("Share", href="#"))
    ],
    brand='Sustain our Soil for our Food',
    color="dark",
    dark=True,
    class_name="fixed-top",
)

appSubheading = html.Div([
    html.H5("Organic carbon occurs naturally in soil, but whether it presents a threat or a service to humans depends on YOU.",
    style={'text-align': 'left'})
])

learnMore = dbc.Button("Learn more about soil health, and how you can help.", id="learn-more-button", color="link", size="md")

whyCarbon = dbc.Card(
    html.Div(children=[
        html.H5("Carbon has a superpower.",
        style={'text-align': 'left'}
        ),
        html.P("Often called the element or giver of life, carbon is critical to life supporting processes because it can bond to many other elements essentially as a building block of large and complex compounds that make up living things––including soil, and the plants and animals in the food chain. Soil organic carbon is left in the soil by the processes collectively called the Carbon Cycle, which includes both the growth and death of plants, animals, and other organisms.",
        style={'text-align': 'left'}
        ),
        html.P("Soil organic carbon (SOC) indicates soil's ability to hold water and nutrients that sustain plants in natural and farming settings. As an indicator of soil's overall organic matter, it also builds soil structure that reduces erosion leading to improved water quality and greater resilience from storms.",
        style={'text-align': 'left'}
        ),
        html.P("Including its mineral inorganic carbon parts, our soil holds the largest amount of carbon in Earth's ecosystem, and its release––through mismanagement from a lack of knowledge and the removal of forests and wetlands––is a great risk to increasing carbon dioxide in the atmosphere and speeding up climate change.",
        style={'text-align': 'left'}
        ),
        html.P("Whether your food comes from across the globe or your own garden, you have an opportunity to restore and ensure soil health to fill bellies all over the world with nutritious foods for years to come. By learning more, you can have an impact on soil health, and together we may even save the world one plate at a time.",
        style={'text-align': 'left'}
        )
    ]),
    body=True
)

# introduce the controls section, used with map
controlsIntro =  html.Div(children=[
    # add a brief instructive subheading as a label introducing the map
    html.H6('Explore how much of the soil where your food comes from is made up of organic carbon.'
    ),
    # # give more text tips on how to easily find countries
    # html.P('Type in the boxes below to search choices in the drop down menus.'
    # )
])

dropdownCountry = html.Div(children=[
    # add an intructive label before dropdown
    dbc.Label('To begin, choose where you eat.'
    ),
    # add a dropdown for audience member using app to select country where they generally eat
    dcc.Dropdown(id='trade_partner_country_dropdown', 
                 options=[{'label': country, 'value': country}
                          # series values needed to be sorted first before taking unique to prevent errors
                          for country in dffood['Partner Countries'].sort_values().unique()
                 ],
                 # value='United States', # None so no selection is defaulted upon each load of the app page
                 placeholder='Country',
                 multi=False, # True to allow multiple Country selections
                 searchable=True, # allows type in search to filter dropdown options that show
                 clearable=True, # shows an 'X' option to clear selection once selection is made
                 persistence=True, # True is required to use a persistence_type
                 persistence_type='session', # remembers dropdown value selection until browser tab is closed (saves after refresh) 
                 style={"width": "65%"}
    ),
    html.Br()
])

dropdownFood = html.Div(children=[
    # add a brief instructive subheading as a label
    html.Label('Then, choose a food you enjoy.', style={'text-align': 'left'}
    ),
    # add a dropdown for audience member using app to select a food they frequently eat
    dcc.Dropdown(id='food_dropdown',
                 options=[], # empty because callbacks are populating this below, based on country selection(s)
                #  options=[{'label': food, 'value': food}
                #           # series values needed to be sorted first before taking unique to prevent errors
                #           for food in dffood['Item'].sort_values().unique()
                #  ],
                 placeholder='Food',
                 searchable=True, 
                 clearable=True, # shows an 'X' option to clear selection once selection is made
                 persistence=True, # True is required to use a persistence_type
                 persistence_type='session', # remembers dropdown value selection until browser tab is closed (saves after refresh) 
                 style={"width": "65%"}
    ),
    html.Br()
])

mapExplorer = dbc.Container([
    html.Div([
        dcc.Graph(
            id='map-socd',
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Dots on the map vary in size by the location's soil organic carbon density (SOCD), which can be understood as how much of the soil is made up of organic carbon, from the ground surface down to 4.5 centimeters deep. These density estimates are by global leading scientists from the available worldwide soil data––collected and mathematically modelled––and are expressed in metric tonnes (t ha-1), which are equal to about 1,000 kilograms or aproximately 2,205 pounds.", 
        style={'text-align': 'left'}),
        html.P("Learn more about carbon and its importance in soil below.",
        style={'text-align': 'left'}),
        html.P("Data citation: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, 6: 249-263.",
        style={'text-align': 'left'}),
    ]),
    html.Br()
])

densityRanges = dbc.Container([
    html.Div([
        dcc.Graph(
            id="SOCD-bar-chart",
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Bars show the global range of soil organic carbon density on land.",
        style={'text-align': 'left'}),
        html.P("Data citation: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, 6: 249-263.",
        style={'text-align': 'left'}),
    ]),
    html.Br()
])

riskFoods = dbc.Container([
    html.Div([
        dcc.Graph(
            id="food-bar-chart",
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Bars show the world's foods from countries with the lowest soil carbon densities on average.",
        style={'text-align': 'left'}),
        html.P("Data citation: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, 6: 249-263.",
        style={'text-align': 'left'}),
    ]),
    html.Br()
])

controls = dbc.CardBody([controlsIntro, dropdownCountry, dropdownFood])

tab1 = dbc.Tab([densityRanges], label="Density Ranges")
tab2 = dbc.Tab([riskFoods], label="At Risk Foods")
tab3 = dbc.Tab([whyCarbon], label="Why Carbon?")
tabs = dbc.Tabs([tab1, tab2, tab3])

# create the app's layout with the named variables
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(navbar,
                width=12)
            ]
        ),
        dbc.Row(
            [
                dbc.Col(appSubheading, 
                width=12)
            ]
        ),
        dbc.Row(
            [
                dbc.Col(controls, width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(mapExplorer, width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(learnMore,
                width={'size': 9, 'offset': 2}, md={'size': 5, 'offset': 6}
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Br(), width=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(tabs, width=12),
            ]
        ),
    ], 
    fluid=True,
    className="dbc"
)

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
        # if bool(selected_food): # if no food is selected, this is falsy so no filtering
        if selected_food is None: # if no food is selected, # format that worked in reprex solution
        # if len(selected_food) == 0: # if no food is selected # commented out due to this line returning 'TypeError: object of type 'NoneType' has no len()' 
            return dash.no_update # dash.no_update prevents any single output updating    
    else:
        # take a subset of food trade data including rows containing Partner Countries matching country dropdown selection, 
        # using == because selected_partner_country is a string, not a list (with a list use .isin); using binary OR '&' instead of AND 'I'
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