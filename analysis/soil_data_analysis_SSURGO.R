# modeled after tutorial at http://ncss-tech.github.io/AQP/soilDB/SDA-tutorial.html
# Soil data presented were derived from the 100+ year efforts of 
# the National Cooperative Soil Survey, c/o USDA-NRCS

# # install the packages
# # only once if you have not previously installed these
# install.packages('aqp', dep=TRUE)
# install.packages('soilDB', dep=TRUE)
# install.packages('sharpshootR', dep=TRUE)
# install.packages('plyr', dep=TRUE)
# install.packages('RColorBrewer', dep=TRUE)
# install.packages('httr', dep=TRUE)
# install.packages('rgdal', dep=TRUE)
# install.packages('raster', dep=TRUE)
# install.packages('rgeos', dep=TRUE)
# install.packages("kableExtra")
# # get latest versions from GitHub
# install.packages('devtools', dep=TRUE)
# devtools::install_github("ncss-tech/soilDB", dependencies=FALSE, upgrade_dependencies=FALSE)

# load packages
library(aqp)
library(plyr)
library(cluster)
library(ape)
library(colorspace)
library(soilDB)
library(sharpshootR)
library(plyr)
library(RColorBrewer)
library(latticeExtra)
library(httr)
library(rgdal)
library(raster)
library(rgeos)
library(kableExtra)

# warmup with an example plot showing soil color signatures
# using some of the aqp package's built-in data
# according to D.E. Beaudette, Source colors are in sRGB (D65) colorspace, as 
# converted from Munsell notation using aqp::munsell2rgb().
# source: http://ncss-tech.github.io/AQP/aqp/soil-color-signatures.html
data(sp1)
sp1$soil_color <- with(sp1, munsell2rgb(hue, value, chroma))
depths(sp1) <- id ~ top + bottom
plot(sp1)

# Colors from Official Series Descriptions
s.list <- c('amador', 'redding', 'pentz', 'willows', 'pardee', 'yolo', 'hanford', 'cecil', 'sycamore', 'KLAMATH', 'MOGLIA', 'vleck', 'drummer', 'CANEYHEAD', 'musick', 'sierra', 'HAYNER', 'zook', 'argonaut', 'PALAU')

# get these soil series
s <- fetchOSD(s.list)

# manually convert Munsell -> sRGB
rgb.data <- munsell2rgb(s$hue, s$value, s$chroma, return_triplets = TRUE)
s$r <- rgb.data$r
s$g <- rgb.data$g
s$b <- rgb.data$b

# Look at full range of OSD colors in this set.
# Colors, arranged by ΔE00.
previewColors(s$soil_color)

# When was each survey area last exported to SSURGO? Show most recent at top.
SDA_query("SELECT areasymbol, saverest FROM sacatalog WHERE areasymbol != 'US' ORDER BY saverest desc")

# When was the most recent updated survey in Vermont, if any exist?
SDA_query("SELECT areasymbol, saverest FROM sacatalog WHERE areasymbol LIKE 'VT%' ORDER BY saverest DESC")[1, ]

# show all Vermont
SDA_query("SELECT areasymbol, saverest FROM sacatalog WHERE areasymbol LIKE 'VT%' ORDER BY areasymbol DESC")

# get a list of map units that contain carbon as a component
q <- "SELECT
muname, mapunit.mukey, cokey, compname, comppct_r
FROM legend
INNER JOIN mapunit ON mapunit.lkey = legend.lkey
INNER JOIN component on mapunit.mukey = component.mukey
WHERE
-- explicitly exclude STATSGO records saved in same table
legend.areasymbol != 'US'
AND compname LIKE '%carbon%'"

# run the query
res <- SDA_query(q)

# check the head of the query results
# ?kable
kable(head(res))

head(res)

# have a look at the interpretations table
# example for map area MO123
SDA_query("SELECT l.areasymbol AS Area_symbol, m.musym AS Map_unit_symbol, m.mukey AS MUKEY,
c.compname AS Component_name, c.comppct_r AS Component_percent, c.majcompflag AS Major_Component,
ci.mrulename AS Rule_name, ci.ruledepth AS Rule_depth, interplr AS Rating, interplrc AS Rating_class
FROM legend AS l
INNER JOIN mapunit AS m ON l.lkey = m.lkey AND l.areasymbol LIKE 'MO123'
INNER JOIN component AS c ON m.mukey = c.mukey AND c.majcompflag='yes'
INNER JOIN cointerp AS ci ON c.cokey = ci.cokey AND ci.ruledepth=0 AND mrulename LIKE '%lawn%'
ORDER by m.musym, c.comppct_r")

# list of distinct interpretation rule names and component names
# this query timed out
# SDA_query("SELECT DISTINCT c.compname AS Component_name, ci.mrulename AS Rule_name
# FROM legend AS l
# INNER JOIN mapunit AS m ON l.lkey = m.lkey AND l.areasymbol != 'US'
# INNER JOIN component AS c ON m.mukey = c.mukey
# INNER JOIN cointerp AS ci ON c.cokey = ci.cokey
# ORDER by Component_name, Rule_name")

# list of interpretation rule names and component names
# try without distinct
# nope this timed out as well
# SDA_query("SELECT c.compname AS Component_name, ci.mrulename AS Rule_name
# FROM legend AS l
# INNER JOIN mapunit AS m ON l.lkey = m.lkey AND l.areasymbol != 'US'
# INNER JOIN component AS c ON m.mukey = c.mukey
# INNER JOIN cointerp AS ci ON c.cokey = ci.cokey
# ORDER by Component_name, Rule_name")

# list of distinct interpretation rule names and component names
# does removing filters speed it up? nope this also timed out
# SDA_query("SELECT DISTINCT c.compname AS Component_name, ci.mrulename AS Rule_name
# FROM legend AS l
# INNER JOIN mapunit AS m ON l.lkey = m.lkey
# INNER JOIN component AS c ON m.mukey = c.mukey
# INNER JOIN cointerp AS ci ON c.cokey = ci.cokey
# ORDER by Component_name, Rule_name")
