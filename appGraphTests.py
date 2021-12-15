# ----------------------------------------------------------------------------------------
# prepare environment (boilerplate)

# import the required packages using their usual aliases
import dash
from dash import dcc, html, Input, Output  # State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import humanize

# read token string with your access mapbox token from a hidden file
# saved in environment's root directory same as where this app.py file is
# if you're using GitHub make sure to add '*.mapbox_token' to your .gitignore file
# to prevent your private credentials from being publicly viewed or uploaded to GitHub
mapbox_access_token = open(".mapbox_token").read()

# ----------------------------------------------------------------------------------------
# -- call the data
# -- read the food trade matrix data into pandas from CSV file of 2019 export quantities (exported from analysis in Jupyter Notebook)
# prepared using original dataset FAOSTAT Detailed trade matrix: All Data Normalized from https://fenixservices.fao.org/faostat/static/bulkdownloads/Trade_DetailedTradeMatrix_E_All_Data_(Normalized).zip
# with appended key demographics from FAOSTAT Key dataset (in Jupyter Notebook)
# # full dataset
dffood = pd.read_csv('./data/dffood.csv')

# -- read the 4.5 depth soil organic carbon density (%) measurements pre-filtered for audience China's and U.S.'s food's trade export Reporter Countries (exported from analysis in Jupyter Notebook)
# prepared using original dataset Soil organic carbon density: SOCD5min.zip from http://globalchange.bnu.edu.cn/research/soilw
# with appended country name and ISO3 code from GeoPandas embedded World dataset
dfsoil = pd.read_csv('./data/dfsoil_subUSCN.csv')

# ----------------------------------------------------------------------------------------
# create (instantiate) the app,
# using the Bootstrap MORPH theme, Slate (dark) or Flatly (light) theme or Darkly (its dark counterpart) to align with my llc website in development with Flatly (dadeda.design)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH],
                meta_tags=[{'name': 'viewport',
                            # initial-scale is the initial zoom on each device on load
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]
                )

# ----------------------------------------------------------------------------------------
# named variables for the app's layout
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Contact", href="#")),  # mailto link, github issues, and/or "http://kathrynhurchla.com/", target="_blank"),
        dbc.NavItem(dbc.NavLink("Share", href="#"))
    ],
    brand='Sustain our Soil for our Food',
    color='#483628',  # "dark", #hex code color matching text in graphs, a dark orange brown; "dark" is MORPH theme option and a dark charcoal
    dark=True,
    class_name="fixed-top",
)

appSubheading = dbc.Container(
    html.Div([
        html.H5("Organic carbon occurs naturally in soil, but whether it presents a threat or a service to humans depends on YOU.")
        ])
)

learnMore = dbc.Button("Learn more about soil health, and how you can help.", id="learn-more-button", color="link", size="md", class_name="btn btn-link")

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
    body=True,
    color="light",
    class_name="card bg-light mb-3"
)

# dropdownCountry = dbc.CardBody(
#     html.Div(children=[
#         # add an intructive label before dropdown
#         dbc.Label('Choose where you eat.'
#                   ),
#         # add a dropdown for audience member using app to select country where they generally eat
#         dcc.Dropdown(id='trade_partner_country_dropdown',
#                      options=[{'label': country, 'value': country}
#                               # series values needed to be sorted first before taking unique to prevent errors
#                               for country in ['China, Hong Kong SAR', 'China, Macao SAR', 'China, Taiwan Province of', 'China, mainland', 'United States of America']  # for full list use: dffood['Partner_Country_name'].sort_values().unique()
#                               ],
#                      # value='United States', # None so no selection is defaulted upon each load of the app page
#                      placeholder='Country',
#                      multi=False,  # True to allow multiple Country selections
#                      searchable=True,  # allows type in search to filter dropdown options that show
#                      clearable=True,  # shows an 'X' option to clear selection once selection is made
#                      persistence=True,  # True is required to use a persistence_type
#                      persistence_type='session',  # remembers dropdown value selection until browser tab is closed (saves after refresh)
#                      style={"width": "auto%"}
#                      )
#     ])
# )

# dropdownFood = dbc.CardBody(
#     html.Div(children=[
#         # add a brief instructive subheading as a label
#         dbc.Label('Then, choose a food.', style={'text-align': 'left'}
#                   ),
#         # add a dropdown for audience member using app to select a food they frequently eat
#         dcc.Dropdown(id='food_dropdown',
#                      options=[],  # empty because callbacks are populating this below, based on country selection(s)
#                      #  options=[{'label': food, 'value': food}
#                      #           # series values needed to be sorted first before taking unique to prevent errors
#                      #           for food in dffood['Item'].sort_values().unique()
#                      #  ],
#                      placeholder='Food',
#                      searchable=True,
#                      clearable=True,  # shows an 'X' option to clear selection once selection is made
#                      persistence=True,  # True is required to use a persistence_type
#                      persistence_type='session',  # remembers dropdown value selection until browser tab is closed (saves after refresh)
#                      style={"width": "auto%"}
#                      )
#     ])
# )

dropdownReporterCountry = dbc.CardBody(
    html.Div(children=[
        # add a brief instructive subheading as a label
        dbc.Label('Choose a trade partner.', style={'text-align': 'left'}
                  ),
        # add a dropdown for audience member using app to select a reporter country (their partner who exports the food they've chosen to their country)
        dcc.Dropdown(id='reporter_country_dropdown',
                     options=[{'label': country, 'value': country}
                     # series values needed to be sorted first before taking unique to prevent errors
                     for country in dfsoil['Reporter_Country_name'].sort_values().unique()],
                     placeholder='Trade Partner',
                     searchable=True,
                     clearable=True,  # shows an 'X' option to clear selection once selection is made
                     persistence=True,  # True is required to use a persistence_type
                     persistence_type='session',  # remembers dropdown value selection until browser tab is closed (saves after refresh)
                     style={"width": "auto%"}
                     )
    ])
)


controls = dbc.CardGroup([dropdownReporterCountry], class_name="card border-primary bg-light mb-2")  # removed both: dropdownCountry, dropdownFood,

mapExplorer = dbc.Card([
    html.Div(children=[
        html.P('Explore how much of the soil where your food comes from is made up of organic carbon.',
               className="lead"
               ),
        html.Div(controls),
        html.Div(id='map-socd'
                 # dcc.Graph(
                 #     id='map-socd',
                 #     config={'displayModeBar': True, 'scrollZoom': True}
                 )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Dots on the map vary in size by the location's soil organic carbon density (SOCD), which can be understood as how much of the soil is made up of organic carbon, from the ground surface down to 4.5 centimeters deep. These density estimates are by global leading scientists from the available worldwide soil data––collected and mathematically modelled––and are expressed in metric tonnes per hectare (t ha-1), which are equal to about 1,000 kilograms or aproximately 2,205 pounds.",
               style={'text-align': 'left'}),
        html.P("Read more about carbon's importance in soil below.",
               style={'text-align': 'left'}),
        html.P(children=[
            "Data source: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, ",
            html.A("6: 249-263.",
                   href='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2013MS000293',
                   target='_blank'  # opens link in new tab or window
                   )
        ],
            style={'text-align': 'left'}),
    ]),
    # html.Br()
], body=True)

# --------------------------SOIL BAR graph--------------------------
# take the mean SOCD by grouping soil dataframe by Country and append the mean as a column
dfsoil['SOCDcountryMean'] = dfsoil['Reporter_Country_SOCD_depth4_5'].groupby(dfsoil['Reporter_Country_name']).transform('mean')
# drop the raw SOCD values from the subset of soil data; used in density ranges bar chart
dfsoilMeans = dfsoil.drop_duplicates(subset=['Reporter_Country_name', 'Reporter_Country_continent', 'SOCDcountryMean', 'Reporter_Country_pop_est']).drop(['Reporter_Country_SOCD_depth4_5'], axis=1).sort_values(by=['SOCDcountryMean', 'Reporter_Country_continent', 'Reporter_Country_name'], ascending=(False, True, True))
dfsoilMeansMaxOrder = ['Africa', 'Oceania', 'South America', 'Asia', 'North America', 'Europe']
# make numbers into a more human readable format, e.g., transform 12345591313 to '12.3 billion' for hover info
dfsoilMeans['humanPop'] = dfsoilMeans['Reporter_Country_pop_est'].apply(lambda x: humanize.intword(x))

# make a bar chart showing range of mean by countries, overlay countries within continent group to retain mean y axis levels
rangeSOCDfig = px.bar(dfsoilMeans, x='Reporter_Country_continent', y='SOCDcountryMean', color='SOCDcountryMean', barmode='overlay',
                      # set bolded title in hover text, and make a list of columns to customize how they appear in hover text
                      custom_data=['Reporter_Country_name',
                                   'Reporter_Country_continent',
                                   'SOCDcountryMean',
                                   'humanPop'
                                   ],
                      color_continuous_scale=px.colors.sequential.speed,  # alternately use turbid for more muted yellows to browns (speed for yellow to green to black scale)
                      # a better label that will display over color legend
                      labels={'SOCDcountryMean': 'Avg.<br>SOCD'},
                      # lower opacity to help see variations of color between countries as means change
                      opacity=0.20
                      )
# sort bars by mean SOCD, and suppress redundant axis titles, instead of xaxis={'categoryorder': 'mean ascending'} I pre-sorted the dataframe above, but still force sort here by explicit names
rangeSOCDfig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': dfsoilMeansMaxOrder},
                           xaxis_title=None, yaxis_title=None,  # removed xaxis_tickangle=-45, # used to angle longer/more xaxis labels
                           paper_bgcolor='#e8ece8',  # next tint variation up from a low tint of #dadeda
                           plot_bgcolor='#f7f5fc',  # violet tone of medium purple to help greens pop forward
                           yaxis={'gridcolor': '#e8ece8'},  # match grid lines shown to background to appear as showing through
                           font={'color': '#483628'})  # a dark shade of orange that appears dark brown
rangeSOCDfig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{customdata[0]} </b><br>",  # bolded hover title included, since the separate hover_name is superseced by hovertemplae
        "%{customdata[1]}",  # Continent value with no label
        "Average SOCD: %{customdata[2]:.1f} t ha<sup>−1</sup>",  # with html <sup> superscript tag in abbr. metric tonnes per hectare (t ha-1) t ha<sup>−1</sup> formatted to 2 decimals
        "Estimated Population (2019): %{customdata[3]} people"  # in humanized format
    ])
)


densityRanges = dbc.Card([
    html.Div(children=[
        html.H5("Range of Average Soil Organic Carbon Density (SOCD) Worldwide"
                ),
        dcc.Graph(figure=rangeSOCDfig,
                  id="SOCD-bar-chart",
                  config={'displayModeBar': True, 'scrollZoom': True}
                  )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Bars show the range of soil organic carbon density on land as a mean average within each country in metric tonnes per hectare (t ha-1), which are equal to about 1,000 kilograms or aproximately 2,205 pounds. Hover over any bar to view details for specific countries.",
               style={'text-align': 'left'}),
        html.P(children=[
            "Data source: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, ",
            html.A("6: 249-263.",
                   href='https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2013MS000293',
                   target='_blank'  # opens link in new tab or window
                   )
            ],
               style={'text-align': 'left'}),
    ]),
    html.Br()
], body=True)

# --------------------------FOOD TRADE graph--------------------------

# take the sum total of exported tonnes by grouping food dataframe by Partner (importing) Country and append the sum as a column
dffood['Export_Quantity_Sum'] = dffood['Export_Quantity_2019_Value_tonnes'].groupby(dffood['Partner_Country_name']).transform('sum')
# take the distinct count of exported items by grouping food dataframe by Reporter (exporting) Country and append the count as a column
dffood['Export_Items_Count'] = dffood['Item'].groupby(dffood['Partner_Country_name']).transform('nunique')
# for a 2D histogram density heatmap, do not drop the raw quantity which is aggregated in the chart; the appended pre-aggregated value 'Export_Quantity_Sum' will be used in labels
# # drop the raw quantity values from the subset of food data; used in food risk chart
# dffoodAggs = dffood.drop_duplicates(subset=['Reporter_Country_name_x', 'Reporter_Country_continent', 'Export_Quantity_Sum', 'Reporter_Country_pop_est', 'Export_Items_Count']).drop(['Export_Quantity_2019_Value_tonnes'], axis = 1).sort_values(by=['Export_Quantity_Sum', 'Export_Items_Count', 'Reporter_Country_continent', 'Reporter_Country_name_x'], ascending= (False, False, True, True))
# dffoodAggsMaxOrder = ['Africa', 'Oceania', 'South America', 'Asia', 'North America', 'Europe']
# make numbers into a more human readable format, e.g., transform 12345591313 to '12.3 billion' for hover info
# dffood['humanPop'] = dffood['Reporter_Country_pop_est'].apply(lambda x: humanize.intword(x))
dffood['tradeVolume'] = dffood['Export_Quantity_Sum'].apply(lambda x: humanize.intword(x))

# customdata = ['Reporter_Country_name_x',
#               'Reporter_Country_continent',
#               'tradeVolume',
#               'Export_Items_Count',
#               'humanPop'
#               ]

# make a quadrant scatterplot or heat map of food import volume and population
# # try a density heatmap 2D histogram
# RiskFoodsFig = px.density_heatmap(dffood, x='Export_Items_Count', y='Reporter_Country_pop_est', z='Export_Quantity_2019_Value_tonnes', histfunc="sum",
#                                              # customdata = ['Reporter_Country_name_x',
#                                              #               'Reporter_Country_continent',
#                                              #               'tradeVolume',
#                                              #               'Export_Items_Count',
#                                              #               'humanPop'
#                                              #               ],
#                                   color_continuous_scale=px.colors.sequential.speed, # alternately use turbid for more muted yellows to browns (speed for yellow to green to black scale)
#                                   # a better label that will display over color legend
#                                   labels={'Export_Quantity_2019_Value_tonnes': 'food<br>exported (tonnes)'},
#                                   nbinsx=20,
#                                   nbinsy=20
#                                   )

# scatterplot
# note ignoring continent, population because I found that they contain NaN null values because the world dataset did not recognize some countries or units coded as countries in the UN food data
RiskFoodsFig = px.scatter(dffood, x='Export_Items_Count', y='Export_Quantity_Sum', size='Export_Quantity_Sum',  # , y='Reporter_Country_pop_est', size='Export_Quantity_Sum', color='Reporter_Country_continent', symbol='Reporter_Country_continent',
                          custom_data=['Partner_Country_name',  # 'Reporter_Country_name_x',
                                       # 'Reporter_Country_continent',
                                       'Export_Quantity_Sum',  # 'tradeVolume' removed because flagged 0 values were causing NaN throughout series,
                                       'Export_Items_Count'
                                       # 'humanPop'
                                       ]
                          # color_continuous_scale=px.colors.sequential.speed, # alternately use turbid for more muted yellows to browns (speed for yellow to green to black scale)
                          # a better label that can be displayed in hover info or over a color legend
                          # labels={'Export_Quantity_2019_Value_tonnes': 'food<br>exported (tonnes)'},
                          )

# sort bars by mean SOCD, and suppress redundant axis titles, instead of xaxis={'categoryorder': 'mean ascending'} I pre-sorted the dataframe above, but still force sort here by explicit names
RiskFoodsFig.update_layout(  # xaxis={'categoryorder': 'array', 'categoryarray': dffoodAggsMaxOrder},
                           xaxis_title='Diversity of Foods Imported (How many unique items?)',  # Exported (How many unique items?)',
                           title='Volume as Total Quantity of Foods Imported (M represents Millions of tonnes)',
                           yaxis_title='',  # yaxis_title= 'Total quantity of foods imported (tonnes)', # exported (tonnes)', # yaxis_title='Population', # removed xaxis_tickangle=-45, # used to angle longer/more xaxis labels
                           paper_bgcolor='#e8ece8',  # next tint variation up from a low tint of #dadeda
                           plot_bgcolor='#f7f5fc',  # violet tone of medium purple to help greens pop forward
                           yaxis={'gridcolor': '#e8ece8'},  # match grid lines shown to background to appear as showing through
                           font={'color': '#483628'})  # a dark shade of orange that appears dark brown
RiskFoodsFig.update_traces(
    # hard code single point color
    marker=dict(
        color='#a99e54',
        sizemin=10
    ),
    # set bolded title in hover text, and make a list of columns to customize how they appear in hover text
    hovertemplate="<br>".join([
        "<b>%{customdata[0]} </b><br>",  # bolded hover title included, since the separate hover_name is superseced by hovertemplae
        # "%{customdata[1]}", # Continent value with no label # removed until NaN or empty values can be resolved
        "Trade Volume: %{customdata[1]:,} tonnes imported",  # %{customdata[2]:,} tonnes exported", # note html tags can be used in string; comma sep formatted; note with tradeVolume use format .1f to 1 decimals
        "Trade Diversity: %{customdata[2]:} unique food products imported",  # %{customdata[3]:} unique food products exported",
        # "Estimated Population (2019): %{customdata[4]} people" # in humanized format # removed until NaN or empty values can be resolved
    ])
)

riskFoods = dbc.Card([
    html.Div(children=[
        html.H5("Food Security Risk Analysis by Volume & Diversity of Food Trade Reliance"
                ),
        dcc.Graph(figure=RiskFoodsFig,
                  id="food-quadrant-chart",
                  config={'displayModeBar': True, 'scrollZoom': True}
                  )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Points show where each country falls in relations to these two major trade metrics as indicators of risk for a country's ability to feed its population. Countries in the upper right corner can generally be understood to be most at risk if food trade lines are affected by decreased production.",
               style={'text-align': 'left'}),
        html.P("All food products traded between countries are included in the total summary of items imported, in 2019, as measured in metric tonnes. While soil organic carbon content is a major factor determining agricultural productivity, those levels are not directly shown in this graph and there are many factors that can lead to trade volatility",  # The major grid lines dividing the four sections are set at the median, in other words the middle, of that range of global values as a benchmark to divide high or low in population and trade dependency, in relation to other countries.",
               style={'text-align': 'left'}),
        html.P(children=["Food and Agriculture Organization of the United Nations. (2020). FAOSTAT Detailed trade matrix: All Data Normalized. ",
                         html.A('https://www.fao.org/faostat/en/#data/TM',
                                href='https://www.fao.org/faostat/en/#data/TM',
                                target="_blank"  # opens link in new tab or window
                                )
                         ],
               style={'text-align': 'left'}
               )
    ]),
    html.Br()
], body=True)

tab1 = dbc.Tab([densityRanges], label="Density Ranges")  # this was for when densityRanges was in a container instead of card: #, style={"padding-top": 20})
tab2 = dbc.Tab([riskFoods], label="At Risk Foods")  # this was for when riskFoods was in a container instead of card: #, style={"padding-top": 20})
tab3 = dbc.Tab([whyCarbon], label="Why Carbon?")
tabs = dbc.Tabs(children=[tab1, tab2, tab3])

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
                        width={"size": "auto", "offset": 0},
                        md={"size": "auto", "offset": 1},
                        xxl={"size": "auto", "offset": 2}
                        ),
            ],
            justify="left",
            style={"padding-top": 95, "padding-bottom": 0}
        ),
        dbc.Row(
            [
                dbc.Col(mapExplorer,
                        width={"size": 11, "offset": 0}
                        )
            ],
            justify="center",
            style={"padding-top": 10, "padding-bottom": 25}
        ),
        dbc.Row(
            [
                dbc.Col(learnMore,
                        width={'size': 9, 'offset': 2}, md={'size': 5, 'offset': 6}
                        )
            ],
            style={"padding-top": 10, "padding-bottom": 10}
        ),
        dbc.Row(
            [
                dbc.Col(html.Br(),
                        width=12
                        )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Container(
                        tabs),
                    width={"size": 11, "offset": 0}
                )
            ],
            justify="center",
        ),
    ],
    fluid=True,
    className="dbc"
)

# ----------------------------------------------------------------------------------------
# callback decorators and functions
# connecting the Dropdown values to the graph

# # populate the options of food dropdown based on country dropdown selection(s)
#
#
# @app.callback(
#     Output('food_dropdown', 'options'),
#     Input('trade_partner_country_dropdown', 'value')
# )
# def set_food_options(selected_partner_country):
#     # using == because selected_partner_country is a string, not a list (with a list use .isin)
#     dffood_sub = dffood[dffood['Partner_Country_name'] == selected_partner_country]
#     # return a unique list of the food items for that partner country
#     return [{'label': s, 'value': s} for s in sorted(dffood_sub['Item'].unique())]
#
# # populate options for a third dropdown of Reporter countries based on food dropdown selection (and dependent on country dropdown selection)
#
#
# @app.callback(
#     Output('reporter_country_dropdown', 'options'),
#     Input('food_dropdown', 'value')
# )
# def set_reporter_country_options(selected_food):
#     dffood_sub = dffood[dffood['Item'] == selected_food]
#     return [{'label': s, 'value': s} for s in sorted(dffood_sub['Reporter_Country_name_x'].unique())]
#
# # Output of graph; return the selected options from the dropdown menus, and
# # input for the correlating trade Reporter Country(ies)'s all its locations to the map
#
#
# @app.callback(
#     Output('map-socd', 'children'),
#     [Input('trade_partner_country_dropdown', 'value'),
#      Input('food_dropdown', 'value'),
#      Input('reporter_country_dropdown', 'value')]
# )
# def update_selected_reporter_country(selected_partner_country, selected_reporter_country, selected_food):
#     # always make a copy of any dataframe to use in the function
#     # define the subset of data that matches the selected values from both dropdowns
#     dfsoil_sub = dfsoil  # full dataframe with geo points
#     print(dfsoil_sub[(dfsoil_sub['Reporter_Country_name'] == selected_reporter_country)])

# simple selection on country directly
@app.callback(
    Output('map-socd', 'children'),
    [Input('reporter_country_dropdown', 'value')]
)
def update_selected_reporter_country(selected_reporter_country):
    # always make a copy of any dataframe to use in the function
    # define the subset of data that matches the selected values from both dropdown(s)
    dfsoil_sub = dfsoil
    dfsoil_sub1 = dfsoil_sub[(dfsoil_sub['Reporter_Country_name'] == selected_reporter_country)]  # filter dataframe with geo points

    # create figure variables for the graph object
    locations = [go.Scattermapbox(
        name='SOCD at Surface Depth to 4.5cm',
        lon=dfsoil_sub1['Reporter_Country_lon'],
        lat=dfsoil_sub1['Reporter_Country_lat'],
        mode='markers',
        marker=go.scattermapbox.Marker(
                                       size=dfsoil_sub['Reporter_Country_SOCD_depth4_5'],
                                       color='fuchsia',  # bright hue for contrast; organic matter hex color #a99e54 was not visible on map terrain of similar color
                                       opacity=0.7
                                       ),
        hoverinfo='text',
        hovertext=str(dfsoil_sub['Reporter_Country_SOCD_depth4_5']) + ' t ha<sup>−1</sup organic carbon density'
        )
    ]

    # add a mapbox image layer below the data
    layout = go.Layout(
                uirevision='foo',  # preserves state of figure/map after callback activated
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
    return dcc.Graph(config={'displayModeBar': True, 'scrollZoom': True},
                     figure={
                         'data': locations,
                         'layout': layout
                     })

# ----------------------------------------------------------------------------------------
# run the app


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)  # if inside Jupyter Notebook, add use_reloader=False inside parens to turn off reloader
