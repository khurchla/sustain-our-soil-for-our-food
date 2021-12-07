# test the graphs separately standalone mini apps
# import the required packages using their usual aliases
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
# import plotly.graph_objects as go # or plotly.express as px
import plotly.express as px
import pandas as pd

# -- read the 4.5 depth soil organic carbon density (%) measurements to filter for selected food's trade export Reporter Countries (exported from analysis in Jupyter Notebook)
# prepared using original dataset Soil organic carbon density: SOCD5min.zip from http://globalchange.bnu.edu.cn/research/soilw
# # full dataset
# dfsoil = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/gdf2flatsurface.csv')
# smaller test dataset
# dfsoil = pd.read_csv('/Users/kathrynhurchla/Documents/GitHub/sustain-our-soil-for-our-food/data/gdf2flatsurface_top_n_rows.csv')
# make a minimal df for a reprex
dfsoil = pd.DataFrame({'country_name': ['Albania', 'Albania', 'Albania', 'Afghanistan', 'Afghanistan', 'Afghanistan', 'Benin', 'Benin','Benin'],
                      'SOCD': [8, 21, 7, 3, 2, 3, 6, 6, 5],
                      'country_pop_est': [3047987, 3047987, 3047987, 34124811, 34124811, 34124811, 11038805, 11038805, 11038805],
                      'continent': ['Europe', 'Europe', 'Europe', 'Asia', 'Asia', 'Asia', 'Africa', 'Africa', 'Africa']
                      })

# ----------------------------------------------------------------------------------------
# create (instantiate) the app,
# using the Bootstrap MORPH theme, or Flatly (light) theme or Darkly (its dark counterpart) to align with my llc website in development with Flatly (dadeda.design)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH],
                meta_tags=[{'name': 'viewport',
                            # initial-scale is the initial zoom on each device on load
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5'}]
                )

# take the mean SOCD by grouping soil dataframe by Country and append the mean as a column
dfsoil['SOCDcountryMean'] = dfsoil['SOCD'].groupby(dfsoil['country_name']).transform('mean')
# dfsoilMeans = dfsoil[['country_name', 'continent', 'SOCDcountryMean', 'country_pop_est']].value_counts().index.values
dfsoilMeans = dfsoil.drop_duplicates(subset=['country_name', 'continent', 'SOCDcountryMean', 'country_pop_est']).drop(['SOCD'], axis = 1)
print(dfsoilMeans)
# trying it without appending a column worked, but I could not show the mean calculated on the fly in hover_data text
# # take a copy of the dataframe to prevent impacting values in other graphs where it is used 
# dfsoilMean = dfsoil
# dfsoilMean.groupby(dfsoil['country_name'])['SOCD'].mean()

# make a bar chart showing range of mean by countries, 
# with graph objects, textangle wasn't working
# rangeSOCDfig = go.Figure([go.Bar(x=dfsoil['country_name'], y=dfsoil['SOCDcountryMean'], textangle=-45)])
# # sorted asscending by mean, and rotate x axis country labels at an angle
# rangeSOCDfig.update_layout(xaxis={'categoryorder': 'total ascending'})
# with plotly express
rangeSOCDfig = px.bar(dfsoilMeans, x='country_name', y='SOCDcountryMean',
                      # set bolded title in hover text, and make a list of columns to customize how they appear in hover text
                      custom_data=['country_name', 'continent', 'SOCDcountryMean', 'country_pop_est']
                      )
# sort bars by mean SOCD, and suppress redundant axis titles, and angle the x axis labels to be more readable
rangeSOCDfig.update_layout(xaxis={'categoryorder': 'mean ascending'}, xaxis_title=None, yaxis_title=None, xaxis_tickangle=-45)
rangeSOCDfig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{customdata[0]} </b><br>", # bolded hover title included, since the separate hover_name is superseced by hovertemplae
        "%{customdata[1]}", # Continent value with no label
        "Average SOCD: %{customdata[2]} t ha<sup>−1</sup>", # with html <sup> superscript tag in abbr. tonne per hectare
        "Estimated Population (2019): %{customdata[3]:,} people"
    ]) 
) 

densityRanges = dbc.Card([
    html.Div(children=[
        html.H5("Range of Average Soil Organic Carbon Density (SOCD) by Countries"
        ),
        dcc.Graph(figure=rangeSOCDfig,
            id="SOCD-bar-chart",
            config={'displayModeBar': False, 'scrollZoom': True}
        )
    ]),
    html.Br(),

    html.Div(children=[
        html.P("Bars show the global range of soil organic carbon density on land.",
        style={'text-align': 'left'}),
        html.P("Data source: Shangguan, W., Dai, Y., Duan, Q., Liu, B. and Yuan, H., 2014. A Global Soil Data Set for Earth System Modeling. Journal of Advances in Modeling Earth Systems, 6: 249-263.",
        style={'text-align': 'left'}),
    ]),
    html.Br()
], body=True)

tab1 = dbc.Tab([densityRanges], label="Density Ranges") # this was for when densityRanges was in a container instead of card: #, style={"padding-top": 20})
# tab2 = dbc.Tab([riskFoods], label="At Risk Foods") # this was for when riskFoods was in a container instead of card: #, style={"padding-top": 20})
tabs = dbc.Tabs(children=[tab1]) #, tab2])

# create the app's layout with the named variables
app.layout = dbc.Container(
    [
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
# run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=3000)  # if inside Jupyter Notebook, add use_reloader=False inside parens to turn off reloader