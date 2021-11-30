import xarray as xr
# import numpy as np
import pandas as pd
import geopandas as gpd

# read the data file in with xarray and assign it to ds variable
ds = xr.open_dataset("../data/SOCD5min.nc")
# transform it to a dataframe assigned to df variable
df = ds.to_dataframe()

# try the subset to remove na values without going through the flattening of the index first
# it works without resetting the index
df2 = df[~df.SOCD.isna()]

# flatten the index of the overall df2 dataframe (with NaN removed, before summary)
df2flat = df2.reset_index()

# for the dataframe with NA removed
# translate lon and lat columns into a spatial geometry variable in a GeoPandas dataframe
gdf2flat = gpd.GeoDataFrame(df2flat, geometry=gpd.points_from_xy(df2flat.lon, df2flat.lat))

# Set a CRS on the geo dataframe object first
# according to data source documentation, the coordinate system is WGS_1984
# readme file is available at http://globalchange.bnu.edu.cn/download/doc/worldsoil/readme.zip
gdf2flat.crs = "EPSG:4326"

# take only the 4.5 depth records and
# reset the index and drop the extra previous index column
gdf2flatsurface = gdf2flat[gdf2flat['depth'] == 4.5].reset_index(drop=True)

# commented out due to KeyError: "['index'] not found in axis"
# # dropping unnecessary previous 'index' column
# gdf2flatsurface = gdf2flatsurface.drop('index', axis=1)

# use the world dataset from geopandas to get a link of points set 
# to grab each soil measurement location's country from
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# join my points geometry from gdf2flatsurface to the world and 
# get the countries they are residing in using a spatial join (sjoin)
result = gpd.sjoin(gdf2flatsurface, world, how='left').reset_index(drop=True)

# drop NaN i.e. null values from the result of linking gdf2flatsurface to add country from world dataset
# and drop the extra index column
gdf2flatsurfacecountry = result.dropna().reset_index(drop=True)

# rename name column to country_name, in place to replace column name in same column
gdf2flatsurfacecountry.rename(columns={"name": "country_name", "pop_est": "country_pop_est", "iso_a3": "country_iso_a3", "gdp_md_est": "country_gdp_md_est"}, inplace=True)

# load in the food trade detailed matrix copy freshly downloaded from https://www.fao.org/faostat/en/#data/TM to an alternate directory
# adding , encoding = "ISO-8859-1" to resolve "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf4 in position 38698: invalid continuation byte"
# alternately use the alias 'latin' for encoding
dftrade_mx = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/Trade_DetailedTradeMatrix_E_All_Data_(Normalized).csv', encoding = "ISO-8859-1")

# filter for just the 'Export  Quantity' rows by its element code identified earlier
dftrade_mx_xq = dftrade_mx[dftrade_mx['Element Code'] == 5910].reset_index(drop=True)

# drop columns I do not need
dftrade_mx_xq = dftrade_mx_xq.drop('Element Code', axis=1)
dftrade_mx_xq = dftrade_mx_xq.drop('Year Code', axis=1)

# for my web app I will remove the export quantity trade rows where year is not 2019,
# i.e. I will keep only the most recent export dataset available
# naming it to a new dataframe whilst resetting index and dropping the previous index
dftrade_mx_xq2019 = dftrade_mx_xq.drop(dftrade_mx_xq.loc[dftrade_mx_xq['Year']!=2019].index, inplace=False).reset_index(drop=True)

# read in the FAOSTAT key dataset as a variable
faoSTATkey = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/FAOSTAT_data_11-26-2021.csv')

# For dftrade_mx_xq2019:
# using pandas merge function, link the trade matrix reporter country code with key to append its ISO_3 code
# with left data as food trade matrix
dftrade_mx_xq2019ISO3 = pd.merge(left=dftrade_mx_xq2019, right=faoSTATkey[['Country Code','ISO3 Code']],
                                     # key column from left dataframe
                                     left_on='Reporter Country Code',
                                     # key column from right dataframe
                                     right_on='Country Code',
                                     # merge as a 'left' join type, and 
                                     # drop the duplicate key column used for join from right dataframe
                                     how='left').drop('Country Code', 1)

# There is no "China" in the trade matrix. I will fill China, mainland with China's ISO3 code 'CHN'
# find rows with the Reporter Country Code 41 (for China, mainland), 
# locate the 'ISO3 Code' column in those rows and set it to 'CHN'
dftrade_mx_xq2019ISO3.loc[dftrade_mx_xq2019ISO3['Reporter Country Code'] == 41, 'ISO3 Code'] = 'CHN'

# rename appended ISO3 column to clarify that it's for Reporter Country in trade matrix
dftrade_mx_xq2019ISO3.rename(columns={"ISO3 Code": "Reporter Country ISO3"}, inplace=True)

# commented out because it
# stopped here with output in Terminal 'zsh: killed     /Users/kathrynhurchla/opt/anaconda3/envs/envsoil/bin/python'
# using pandas merge function, link the trade matrix and socd dataframes
# with left data as food trade
dftrade_mx_xq2019_socdsurface = pd.merge(left=dftrade_mx_xq2019ISO3, right=gdf2flatsurfacecountry,
                                     left_on='Reporter Country ISO3',
                                     right_on='country_iso_a3', 
                                     # merge as a 'left' join type, and 
                                     # drop the duplicate key column used for join from right dataframe
                                     how='left').drop('country_iso_a3', 1)

# write a CSV of only the 4.5 depth socd merged with food trade data
dftrade_mx_xq2019_socdsurface.to_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/dftrade_mx_xq2019_socdsurface.csv')