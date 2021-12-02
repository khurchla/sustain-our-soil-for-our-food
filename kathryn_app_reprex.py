import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import pandas as pd

# access mapbox token
mapbox_access_token = open(".mapbox_token").read()

# ----------------------------------------------------------------------------------------
app = dash.Dash(__name__)

# ----------------------------------------------------------------------------------------
# -- make minimal food trade dataframe
# represents food exports (I included rows with Reporter Countries that will match countries in dfsoil)
dffood = pd.DataFrame({'Reporter Countries': ['Afghanistan', 'Afghanistan', 'Albania', 'Albania', 'Benin', 'Benin'],
                      'Reporter Country ISO3': ['AFG', 'AFG', 'ALB', 'ALB', 'BEN', 'BEN'],
                      'Partner Countries': ['Armenia', 'Armenia', 'Austria', 'Austria', 'Burkina Faso', 'Colombia'],
                      'Item': ['Prunes', 'Raisins', 'Beans', 'Broccoli', 'Sheanuts', 'Sheanuts']})

# -- make minimal soil dataframe (note the only reason I've kept these separate is that I could not get my full dataframes to merge without crashing)
# represents soil organic carbon density % (SOCD)
dfsoil = pd.DataFrame({'country_name': ['Albania', 'Albania', 'Afghanistan', 'Afghanistan', 'Benin', 'Benin'],
                      'Reporter Country ISO3': ['ALB', 'ALB', 'AFG', 'AFG', 'BEN', 'BEN'],
                      'lon': [19.3256549835205, 19.3256549835205, 60.5537147521972, 60.6368370056152, 0.789650380611419, 0.872771501541137],
                      'lat': [42.1891021728515, 42.1063117980957, 32.9997024536132, 33.9103622436523, 10.4815368652343, 10.8126859664917],
                      'SOCD': [8, 21, 3, 2, 6, 6]})

# ----------------------------------------------------------------------------------------
app.layout = html.Div(children=[
    html.H1('Sustain our Soil for our Food'
    ),
    
    # add a dropdown for audience to select their country
    html.Div(
    dcc.Dropdown(id='trade_partner_country_dropdown', 
                 options=[{'label': country, 'value': country}
                          # using a sorted list of unique countries receiving food exports
                          for country in dffood['Partner Countries'].sort_values().unique()
                 ],
                 placeholder='Select Country',
                 multi=False, # I tried both False, and True to allow multiple Country selections, and still got errors in either case
    ),
    ),
    
    # add a dropdown for audience to select a food
    html.Div(
    dcc.Dropdown(id='food_dropdown',
                 options=[], # empty because callbacks should be populating this below, based on country selection(s)
                 placeholder='Select Food',
    ),
    ),

    html.Div(
        dcc.Graph(
        id='map-socd',
        config={'displayModeBar': False, 'scrollZoom': True}
        )
    ),
])

# ----------------------------------------------------------------------------------------
# populate the options of food dropdown based on countries dropdown selection(s)
@app.callback(
    Output('food_dropdown', 'options'),
    Input('trade_partner_country_dropdown', 'value')
)

def set_food_options(selected_partner_country):
    df_sub = dffood[dffood['Partner Countries'] == selected_partner_country]
    return [{'label': s, 'value': s} for s in sorted(df_sub['Item'].unique())]

# populate initial values of food dropdown
@app.callback(
    Output('food_dropdown', 'value'),
    Input('food_dropdown', 'options')
)

def set_food_value(available_options):
    return [x['value'] for x in available_options]

# Output of graph expected result is locations in Reporter Countries 
# from rows based on dropdowns selections for Partner Countries and food 'Item'
@app.callback(
    Output('map-socd', 'figure'),
    [Input('trade_partner_country_dropdown', 'value'),
     State('food_dropdown', 'value')]
)

# take the subset of data matching the selected values from both dropdowns
def update_selected_trade_partner(selected_partner_country, selected_food):
    dfsoil_sub = dfsoil # copy of full dataframe containing geo points
    if bool(selected_partner_country): # if no country is selected, this is falsy so no filtering
        if len(selected_food) == 0: # if no food is selected, 
            return dash.no_update # dash.no_update prevents any single output updating    
    else:
        # take a subset of food trade data including rows containing Partner Countries matching country dropdown selection, and
        dffood_sub = dffood[(dffood['Partner Countries'] == selected_partner_country) |
                        # including rows containing food item traded matching food dropdown selection
                        (dffood['Item'] == selected_food)]
        # loop over the soil data and return only rows with soil country matching the food trade subset Reporter Country
        # first attempt was: return [{'label': r, 'value': r} for r in dfsoil_sub['country_iso_a3'].isin(dffood_sub['Reporter Country ISO3'])]
        # next attempt was: return [{'label': r, 'value': r} for r in dfsoil_sub['Reporter Country ISO3'].reset_index(drop=True) == dffood_sub['Reporter Country ISO3'].reset_index(drop=True)]
        # next attempt was: return [{'label': r, 'value': r} for r in dfsoil_sub['Reporter Country ISO3'].reset_index(drop=True).equals(dffood_sub['Reporter Country ISO3'].reset_index(drop=True))]
        return [{'label': r, 'value': r} for r in dfsoil_sub.loc[dfsoil_sub['Reporter Country ISO3'].isin(dffood_sub['Reporter Country ISO3'])]]

    # make geopoints data for the graph object from the filtered soil data subset
    locations = [go.Scattermapbox(
                 lon = dfsoil_sub['lon'],
                 lat = dfsoil_sub['lat'],
                 mode = 'markers'             
    )]

    # add a graph layout 
    layout = go.Layout(
                uirevision='foo', # preserves state of figure/map after callback activated
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    style='light'
                ),
    )

    # Return figure
    return {
        'data': locations,
        'layout': layout
    }

# ----------------------------------------------------------------------------------------
# run the app
if __name__ == '__main__':
    app.run_server(debug=True)