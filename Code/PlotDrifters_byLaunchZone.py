# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 12:42:49 2014

@author: Alex
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 12:55:04 2014
This code
 reads a gpx file of drifter data in lat/lon decimal degrees
 resamples to an arbitrary timestep to eliminate noise
 converts points to UTM meters
 calculates distance from point to point
 calculates the compass bearing (0-360 degrees from North(=0deg))
 plots arrows colored by the speed
 plots points colored by the speed
 
Next steps:
select points by:
    day or forcing (Tide,Wind,Wave)
    launch point (if first point in track is in Launchpad...)
        shapefile of polygons: http://matplotlib.org/faq/howto_faq.html#test-whether-a-point-is-inside-a-polygon
    grid cell

Fig 6
plot tracks from different day/forcing
    color by launch point
    limit to 1hour drift time

Fig 7
calculate variance/PCR on the points that meet those criteria
    show ellipse in center of each grid cell
    color ellipse by count of samples (number of points)
Fig 8?
calculate mean heading and mean speed
    show arrow in center of each grid cell (I think you set arrow location to 'midpoint' or something so tail isn't at center of grid)
    size of arrow by mean speed
    color arrow by count of samples (number of points)
 
@author: Alex
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import gpxpy
import shapefile ## from pyshp
import datetime as dt
## My functions:
from DrifterDataAnalysisTools import Drifter_Map, speed_and_bearing, my_parser
from DrifterDataAnalysisTools import point_in_polygon, point_in_gridcell, point_in_launchzone
from DrifterDataAnalysisTools import plot_arrows_by_speed, plot_arrows_by_gridcell, plot_arrows_by_launchzone
from DrifterDataAnalysisTools import label_grid_cells, label_launch_zones
plt.close('all')
pd.set_option('display.large_repr', 'info')

## Set Directories
git=True
if git==True: ## Git repository
    maindir = 'C:/Users/Alex/Documents/GitHub/Faga-alu-Bay-water-circulation/' 
    datadir=maindir+'Data/'
    trackdir = maindir+'Data/AllTracks/'
    GISdir = maindir+'Data/DriftersGIS/'
    figdir = maindir+'Figures/fromAlex/'
    dirs={'main':maindir,'data':datadir,'track':trackdir,'GIS':GISdir,'fig':figdir}
elif git!=True: ## Local folders
    datadir = 'C:/Users/Alex/Desktop/'
    trackdir = 'samoa/DRIFTERS/AllTracks/'
    
## Open Spreadsheet of deployment data
XL = pd.ExcelFile(datadir+'Drifter deployment checklist.xlsx')
DepInfo =  XL.parse('Table',header=1,parse_cols='B:O',index_col=0)
    
#### Read GPX file data of drifter tracks:
gpx = gpxpy.parse(open(trackdir+'All_Tracks_UTM2S.gpx','r')) ## All tracks
#gpx = gpxpy.parse(open(datadir+trackdir+'Dep1.gpx','r')) ## Single track file
tracklist=gpx.tracks[0:] 

###### Open shapefiles for analysis
shapef = shapefile.Reader(GISdir+'Launchpads.shp')
grid = shapefile.Reader(GISdir+'grid100m_geo.shp')
AllPoints = speed_and_bearing(tracklist,launchzoneshape=shapef)
AllPoints = speed_and_bearing_to_file(dirs,tracklist,gridshape=grid,launchzoneshape=shapef)
AllPoints = pd.DataFrame.from_csv(datadir+'AllPoints.csv') 

#### Plot arrows by LaunchZone
Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=True,showBinGrid=False,showLaunchZones=True)  
sc=plot_arrows_by_launchzone(Map,AllPoints)
#### Label Launchzones
label_launch_zones(Map,shapef)


## Title
plt.suptitle("ALL Drifter Tracks Faga'alu February-March 2014" )

plt.show()




