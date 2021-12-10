# import netCDF4 as nc
import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
# import dask.dataframe as dd

# raw data file is not saved in repo, and can be downloaded as a zip file from its source:
# http://globalchange.bnu.edu.cn/research/soilwd.jsp "Soil organic carbon density: SOCD5min.zip"

# read the data file in with xarray and assign it to ds variable
ds = xr.open_dataset("./data/SOCD5min.nc")
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

# use the world dataset from geopandas to get a link of points set 
# to grab each soil measurement location's country from
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# join my points geometry from gdf2flatsurface to the world and 
# get the countries they are residing in using a spatial join (sjoin)
gdf2flatsurfacecountry = gpd.sjoin(gdf2flatsurface, world, how='left').reset_index(drop=True)
# print(result.head())

# rename name column to country_name, in place to replace column name in same column, and 
# rename other columns for clarity after they are merged with food trade data later
gdf2flatsurfacecountry.rename(columns={"continent": "Reporter_Country_continent", "name": "Reporter_Country_name", "pop_est": "Reporter_Country_pop_est", "iso_a3": "Reporter_Country_ISO3", "gdp_md_est": "Reporter_Country_gdp_md_est", "SOCD": "Reporter_Country_SOCD_depth4_5", "lon": "Reporter_Country_lon", "lat": "Reporter_Country_lat"}, inplace=True)

# drop columns I no longer need anymore from soil data to limit size
gdf2flatsurfacecountry1 = gdf2flatsurfacecountry.drop(['geometry', 'index_right', 'depth'], axis=1)

# add a country mean SOCD to soil data, to port over with stats to food data
gdf2flatsurfacecountry['Reporter_Country_SOCD_depth4_5mean'] = gdf2flatsurfacecountry.groupby('Reporter_Country_ISO3').Reporter_Country_SOCD_depth4_5.transform('mean')
# gdf2flatsurfacecountry['Reporter_Country_SOCD_depth4_5mean'].mean()
# gdf2flatsurfacecountry.groupby(['Reporter_Country_ISO3']).mean(['Reporter_Country_SOCD_depth4_5mean'])

# get a unique list of the stats from the soil data for countries, to append to food data for food chart
uniqueCountryStats = pd.DataFrame(gdf2flatsurfacecountry, columns=[
    'Reporter_Country_SOCD_depth4_5mean', 'Reporter_Country_pop_est',
    'Reporter_Country_continent', 'Reporter_Country_name',
    'Reporter_Country_ISO3', 'Reporter_Country_gdp_md_est'
    ])
uniqueCountryStats.drop_duplicates(inplace=True)

# drop NaN i.e. null values from the result of linking gdf2flatsurface to add country from world dataset
# plotting those locations showed they are off land in water areas
# and drop the extra index column
gdf2flatsurfacecountry1 = gdf2flatsurfacecountry.dropna().reset_index(drop=True)
# print(gdf2flatsurfacecountry1.head())

# try converting geopandas dataframe back to standard pandas dataframe before more processing
pddf2flatsurfacecountry = pd.DataFrame(gdf2flatsurfacecountry1)

# limit for scale to US partners in food dataset
UStradepartners = ['need list from other subset']
gdf2flatsurfacecountry1_subsetUS = gdf2flatsurfacecountry1.loc[gdf2flatsurfacecountry1['Reporter_Country_ISO3'].isin(UStradepartners)]

# try to expand to North America partners in food dataset
NAtradepartners = ['need list from other subset']
gdf2flatsurfacecountry1_subsetNA = gdf2flatsurfacecountry1.loc[gdf2flatsurfacecountry1['Reporter_Country_ISO3'].isin(NAtradepartners)]

# write dataframes to file in case the kernel chokes on memory again
# to my other project data folder
gdf2flatsurfacecountry1_subsetUS.to_csv('../data/gdf2flatsurfacecountry1_subsetUS.csv')
gdf2flatsurfacecountry1_subsetNA.to_csv('../data/gdf2flatsurfacecountry1_subsetNA.csv')

# ------------------------------------------------------------------------------------
# load in the food trade detailed matrix copy freshly downloaded from https://www.fao.org/faostat/en/#data/TM to an alternate directory
# adding , encoding = "ISO-8859-1" to resolve "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf4 in position 38698: invalid continuation byte"
# alternately use the alias 'latin' for encoding
dftrade_mx = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/Trade_DetailedTradeMatrix_E_All_Data_(Normalized).csv', encoding = "ISO-8859-1")

# filter for just the 'Export  Quantity' rows by its element code identified earlier
dftrade_mx_xq = dftrade_mx[dftrade_mx['Element Code'] == 5910].reset_index(drop=True)

# # review presence of Kosovo and/or Serbia for alignment with ISO keys
# dftrade_mx_xq[dftrade_mx_xq['Reporter Country Code'].isin(['275','286']) | dftrade_mx_xq['Partner Country Code'].isin(['275','286'])]
# dftemp = dftrade_mx_xq[dftrade_mx_xq['Reporter Countries'].isin(['Kosovo','Serbia', 'Serbia (excluding Kosovo)'])]
# dftemp.groupby(['Reporter Countries', 'Reporter Country Code']).count()

# dftemp1 = dftrade_mx_xq[dftrade_mx_xq['Partner Countries'].isin(['Kosovo','Serbia', 'Serbia (excluding Kosovo)'])]
# dftemp1.groupby(['Partner Countries', 'Partner Country Code']).count()

# rename Value to explicitly specify the type of value, 
# because I will drop Element column which is now only 'Export Quantity'
# and also drop Unit which is now all 'tonnes' (and will be labelled in plots clearly)
dftrade_mx_xq.rename(columns={"Value": "Export_Quantity_2019_Value_tonnes", "Reporter Country Code": "Reporter_Country_Code"}, inplace=True)

# for my web app I will remove the export quantity trade rows where year is not 2019,
# i.e. I will keep only the most recent export dataset available
# naming it to a new dataframe whilst resetting index and dropping the previous index
dftrade_mx_xq2019 = dftrade_mx_xq.drop(dftrade_mx_xq.loc[dftrade_mx_xq['Year']!=2019].index, inplace=False).reset_index(drop=True)

# drop columns from food trade data that I do not need anymore
dftrade_mx_xq2019 = dftrade_mx_xq2019.drop(['Element Code', 'Element', 'Year Code', 'Year', 'Unit', 'Item Code'], axis=1)

# read in the FAOSTAT key dataset as a variable
faoSTATkey = pd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/FAOSTAT_data_11-26-2021.csv')
# rename the country code column to match exactly for merging easier
faoSTATkey.rename(columns={"Country Code": "Reporter_Country_Code", "ISO3 Code": "Reporter_Country_ISO3"}, inplace=True)

# For dftrade_mx_xq2019:
# using pandas merge function, link the trade matrix **reporter country** code with key to append its ISO_3 code,
# not necessary to do this for the partner country because I do not intend to connect that with food trade data
# with left data as food trade matrix
dftrade_mx_xq2019ISO3 = dftrade_mx_xq2019.merge(faoSTATkey[['Reporter_Country_Code','Reporter_Country_ISO3']],
                                     # key column that exists with same name now in both dataframes
                                     how='left',
                                     on='Reporter_Country_Code',
                                     # merge as a 'left' join type, and 
                                     # drop the duplicate key column used for join from right dataframe, duplicate key of same name is dropped by default
                                     )

# rename a few more columns to align across datasets for clarity
dftrade_mx_xq2019ISO3.rename(columns={"Reporter Countries": "Reporter_Country_name", "Partner Countries": "Partner_Country_name"}, inplace=True)

# check column names now
# dftrade_mx_xq2019ISO3.columns

# There is no "China" in the trade matrix. I will fill China, mainland with China's ISO3 code 'CHN'
# find rows with the Reporter Country Code 41 (for China, mainland), 
# locate the 'ISO3 Code' column in those rows and set it to 'CHN'
dftrade_mx_xq2019ISO3.loc[dftrade_mx_xq2019ISO3['Reporter_Country_Code'] == 41, 'Reporter_Country_ISO3'] = 'CHN'

# drop columns I do not need anymore
dftrade_mx_xq2019ISO3 = dftrade_mx_xq2019ISO3.drop(['Reporter_Country_Code', 'Partner Country Code'], axis=1)

# with left data as food trade matrix, merge in unique country stats
dftrade_mx_xq2019ISO3 = dftrade_mx_xq2019ISO3.merge(uniqueCountryStats,
                                     # key column that exists with same name now in both dataframes
                                     how='left',
                                     on='Reporter_Country_ISO3',
                                     # merge as a 'left' join type, and 
                                     # drop the duplicate key column used for join from right dataframe, duplicate key of same name is dropped by default
                                     )

# commented out because it
# stopped here with output in Terminal 'zsh: killed     /Users/kathrynhurchla/opt/anaconda3/envs/envsoil/bin/python'
# # using pandas merge function, link the trade matrix and socd dataframes
# # with left data as food trade
# dftrade_mx_xq2019_socdsurface = pd.merge(dftrade_mx_xq2019ISO3, gdf2flatsurfacecountry,
#                                      on='Reporter_Country_ISO3',
#                                      # merge as a 'left' join type, and 
#                                      # the duplicate key column used for join is dropped by default
#                                      how='left')

# check the data types of gdf2flatsurfacecountry1
# gdf2flatsurfacecountry1.dtypes

# # view the list of variable objects in memory with
# dir()
# # selectively delete things I saved that I no longer need from within this script. 
# # Keep all '__...__' globals and aliases for packages unless I am done with them
# # import native python garbage collector to explicitly invoke it (it runs periodically otherwise to release unreferenced memory)
# import gc
# # review list of tracked object (generation=None) (generation=0) (generation=1) (generation=2)
# gc.get_objects(generation=None)
# # release selected memory
# gc.collect

# write dataframes to file in case the kernel chokes on memory again
# to my other directory circumventing github lfs
dftrade_mx_xq2019ISO3.to_csv('..data/dftrade_mx_xq2019ISO3.csv')

# # check variable object type that should now be a <class 'pandas.core.frame.DataFrame'>
# type(pddf2flatsurfacecountry)
# # then view the data types of the column series to see if any of them are still holding onto geopandas.array type
# pddf2flatsurfacecountry.dtypes

# # rerun the line to export the soil dataframe file to be sure it's as small as possible (not sure if that makes any difference)

# # clear the old gpd from memory now
# del gdf2flatsurfacecountry1
# # release selected memory
# gc.collect

# # if all's good retry the merge now maybe with pandas?...
# # check the keys again
# dftrade_mx_xq2019ISO3['Reporter_Country_ISO3']
# # and this
# pddf2flatsurfacecountry['Reporter_Country_ISO3']

# # double check for missing values using a mask on the pd.series.isna() boolean to return only True records
# before merging (should return 'Empty DataFrame' with list of 'Columns:...')
# pddf2flatsurfacecountry[pddf2flatsurfacecountry.Reporter_Country_ISO3.isna()]
# dftrade_mx_xq2019ISO3[dftrade_mx_xq2019ISO3.Reporter_Country_ISO3.isna()]

# commented out because still crashes with pandas merge
# # with left data as food trade, restructured as in current pandas docs
# dftrade_mx_xq2019_socdsurface = dftrade_mx_xq2019ISO3.merge(pddf2flatsurfacecountry, how='left', on='Reporter_Country_ISO3')

# commented out because crashes merging in dask also
# # try to merge with dask
# dftrade_mx_xq2019_socdsurface = dftrade_mx_xq2019ISO3.merge(pddf2flatsurfacecountry, how='left', on='Reporter_Country_ISO3')

# # # if merge works, print a concise summary of the resulting dataframe
# # dftrade_mx_xq2019_socdsurface.info

# # # if it does not work, try dask to merge these large datasets if needed
# # # first make a Dask collection from each pandas dataframe, and let the defaults set how the chunks are structured
# # ddftrade_mx_xq2019ISO3 = dd.from_pandas(dftrade_mx_xq2019ISO3)
# # ddf2flatsurfacecountry = dd.from_pandas(pddf2flatsurfacecountry)

# # read the csv files into dask dataframes, chunking by file size
# ddf1 = dd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/dftrade_mx_xq2019ISO3.csv', blocksize=25e6)
# ddf2 = dd.read_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/gdf2flatsurfacecountry1.csv', blocksize=25e6)

# # view the index values covered by each partition
# ddf1.known_divisions
# ddf1.divisions
# ddf2.known_divisions
# ddf2.divisions

# # set index for faster processing and merging
# ddf1 = ddf1.set_index('Reporter_Country_ISO3')
# ddf2 = ddf2.set_index('Reporter_Country_ISO3')

# # If your smaller table can easily fit in memory, then you might want to ensure that it is a single partition with the following
# ddf1 = ddf1.repartition(npartitions=1)
# # using dask merge function, link the trade matrix and socd dataframes
# # with left data as food trade, on index
# ddf3 = ddf1.merge(ddf2, how='left', left_index=True, right_index=True)
# # write to files for each partition
# ddf3.to_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/ddf3-*.csv', header_first_partition_only=True)

# # write a CSV of only the 4.5 depth socd merged with food trade data
# # # to my other directory circumventing github lfs
# # dftrade_mx_xq2019_socdsurface.to_csv('/Users/kathrynhurchla/Documents/hack_mylfs_GitHub_projects/dftrade_mx_xq2019_socdsurface.csv')
# # to the data folder in this environment project directory
# dftrade_mx_xq2019_socdsurface.to_csv("../data/dftrade_mx_xq2019_socdsurface.csv")