# Data Sources

This project combines global soil organic carbon data with international food trade data. Raw and processed data files are **not stored in this repository** because of their size (the raw files total several GB). Everything below can be downloaded again from its original source, and the notebooks in [`analysis/`](analysis/) show each processing step.

## Primary datasets

### 1. Soil Organic Carbon Density (SOCD), The Global Soil Dataset for Earth System Modeling
- **Publisher:** Land-Atmosphere Interaction Research Group, Sun Yat-sen University (formerly Beijing Normal University)
- **File used:** `SOCD5min.zip` → `SOCD5min.nc` (NetCDF, about 116 MB), "Soil organic carbon density" at 5 arc-minute resolution
- **Download:** http://globalchange.bnu.edu.cn/research/soilw (listed below the table of 34 soil properties)
- **Documentation:** http://globalchange.bnu.edu.cn/download/doc/worldsoil/readme.zip (coordinate system WGS 1984, EPSG:4326)
- **Citation:** Shangguan, W., Dai, Y., Duan, Q., Liu, B., & Yuan, H. (2014). A global soil data set for earth system modeling. *Journal of Advances in Modeling Earth Systems*, 6, 249–263. https://doi.org/10.1002/2013MS000293
- **Underlying source:** FAO/IIASA/ISRIC/ISS-CAS/JRC, 2012. *Harmonized World Soil Database* (version 1.2). FAO, Rome, Italy and IIASA, Laxenburg, Austria.
- **Used in:** `analysis/soil_data_analysis.ipynb` (exploration), `analysis/food_soil_data_analysis_merge.ipynb` (app data prep)

### 2. FAOSTAT Detailed Trade Matrix (TM)
- **Publisher:** Food and Agriculture Organization of the United Nations (FAO)
- **File used:** "All Data Normalized" bulk download, `Trade_DetailedTradeMatrix_E_All_Data_(Normalized).csv` (about 5 GB)
- **Download:** https://www.fao.org/faostat/en/#data/TM
- **Accessed:** 2021-10-11
- **License:** CC BY-NC-SA 3.0 IGO
- **Used in:** `analysis/food_soil_data_analysis.ipynb`, `analysis/food_soil_data_analysis_merge.ipynb`

### 3. FAOSTAT country and region definitions (country-code key)
- **Publisher:** FAO
- **File used:** `FAOSTAT_data_11-26-2021.csv`, with columns `Country Code, Country, M49 Code, ISO2 Code, ISO3 Code`
- **Download:** FAOSTAT → Definitions and standards → Country/Region (https://www.fao.org/faostat/en/#definitions)
- **Accessed:** 2021-11-26
- **Purpose:** maps FAOSTAT country codes to ISO3 codes so that trade data can be joined to the soil data

### 4. Natural Earth country boundaries (low resolution)
- **Source:** the `naturalearth_lowres` dataset that shipped with GeoPandas at the time (https://www.naturalearthdata.com/). It was removed in GeoPandas 1.0, so download "Admin 0 – Countries" (1:110m) from Natural Earth directly.
- **Purpose:** a spatial join that assigns each soil grid point to a country, and supplies country name, continent, ISO3, population estimate and GDP estimate

## Secondary and exploratory sources

### USDA-NRCS Soil Survey (SSURGO and STATSGO2)
- **Publisher:** National Cooperative Soil Survey, c/o USDA Natural Resources Conservation Service
- **Access:** queried live through the Soil Data Access web service (https://sdmdataaccess.nrcs.usda.gov/) using the R package [`soilDB`](http://ncss-tech.github.io/AQP/soilDB/SDA-tutorial.html) (`SDA_query`, `fetchOSD`)
- **Used in:** `analysis/soil_data_analysis_SSURGO.R`, `.Rmd` and `analysis/soil_data_analysis_STATSGO.Rmd`. Rendered results are in `analysis/reports/`.
- **Note:** this US-only data was explored and then set aside in favor of the global SOCD dataset, which fit the project's global food-trade scope. The R reports used `rgdal` and `rgeos`, which were retired in 2023, so the saved HTML reports are the reliable record of those results.

### FAOSTAT Trade: Crops and Livestock Products (TCL)
- `Trade_Crops_Livestock_E_All_Data_(Normalized).csv`, from https://www.fao.org/faostat/en/#data/TCL
- Explored early on in `analysis/food_soil_data_analysis.ipynb`. It was replaced by the Detailed Trade Matrix, which has country-to-country pairs.

## How the app's data files were produced

The app (`app.py`) reads two files from `./data/`, which aren't included here: `dffood.csv` and `dfsoil_subUSCN_prod.csv`. They're produced by `analysis/food_soil_data_analysis_merge.ipynb`:

| Output file | Produced from | Processing |
|---|---|---|
| `dfsoil.csv` | SOCD5min.nc + Natural Earth | Missing values removed; points converted to geometry (EPSG:4326); kept the top layer only (4.5 cm depth); spatial join to countries; off-land points dropped. Columns: `Reporter_Country_lon, _lat, _SOCD_depth4_5, _pop_est, _continent, _name, _ISO3, _gdp_md_est` |
| `dffood.csv` | Detailed Trade Matrix + country-code key | Kept **Export Quantity** rows only (Element Code 5910), **year 2019** only (the most recent complete year at the time), units in tonnes; joined reporter-country ISO3 codes from the key, with "China, mainland" (code 41) assigned `CHN`. Columns: `Reporter_Country_name, Partner_Country_name, Item, Export_Quantity_2019_Value_tonnes, Flag, Reporter_Country_ISO3, …` |
| `dfsoil_subUS.csv` | `dfsoil.csv` | Soil points limited to countries that export food to the US (FAOSTAT partner area codes 231, 232, 240) |
| `dfsoil_subUSCN.csv` | `dfsoil.csv` | Soil points limited to countries that export food to the US or China (partner codes 231, 232, 240 and 41, 96, 128, 214, 351) |
| `dfsoil_subUSCN_prod.csv` | `dfsoil_subUSCN.csv` | Same size as `dfsoil_subUSCN.csv`. It appears to be a copy renamed for deployment. |

**To reproduce:** download sources 1–3, place `SOCD5min.nc` in `./data/`, and update the absolute file paths in the notebooks (some point to a former local folder, `~/Documents/hack_mylfs_GitHub_projects/`). `analysis/environment.yml` lists the original conda environment (Python 3.9, 2021). Package versions have changed a lot since then.

## Background reading
Reference documents consulted during the research:
- USDA NRCS, *Soil Data Access Query Guide*
- USDA NRCS, *SSURGO Metadata – Table Column Descriptions*
- USDA NRCS, *Annual Data Refresh of Soil Survey Database* (2020)
- FAO, *FAOSTAT Detailed Trade Matrix* metadata (TM)
- Shangguan et al., *The Global Soil Dataset for Earth System Modeling*, the paper above, its supporting information and its readme
