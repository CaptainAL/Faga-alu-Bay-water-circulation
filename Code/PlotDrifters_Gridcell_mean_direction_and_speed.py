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
 

@author: Alex
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy
import gpxpy
import shapefile ## from pyshp
import datetime as dt
## My functions:
from DrifterDataAnalysisTools import Drifter_Map, speed_and_bearing, my_parser
from DrifterDataAnalysisTools import point_in_polygon, point_in_gridcell, point_in_launchzone
from DrifterDataAnalysisTools import plot_arrows_by_speed, plot_arrows_by_gridcell, plot_arrows_by_launchzone
from DrifterDataAnalysisTools import label_grid_cells, label_launch_zones


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

### Read GPX file data of drifter tracks:
gpx = gpxpy.parse(open(trackdir+'All_Tracks_UTM2S.gpx','r')) ## All tracks
#gpx = gpxpy.parse(open(datadir+trackdir+'Dep1.gpx','r')) ## Single track file
tracklist=gpx.tracks[0:] 
##
#### Open shapefiles for analysis
shapef = shapefile.Reader(GISdir+'grid100m_geo.shp')
#AllPoints = speed_and_bearing(tracklist,gridshape=shapef)
AllPoints = pd.DataFrame.from_csv(datadir+'AllPoints.csv') ##in PlotDrifters_byLaunchZone.py

## Select deployments, cut to deployment time
endmembers={"wind":range(9,13),"tide":range(13,21),"wave":range(21,31),"all":range(1,31)} ## range are non inclusive
by_dep='wave'## Set to None if you want to show all the data
if by_dep!=None:
    ## Open Spreadsheet of deployment data
    XL = pd.ExcelFile(datadir+'Drifter deployment checklist.xlsx')
    DepInfo =  XL.parse('Table',header=1,parse_cols='B:O',index_col=1)
    deployments=pd.DataFrame()
    for deployment in DepInfo.iterrows():
        start=my_parser(deployment[1]['Date'],deployment[1]['Start Time']) ##start time from DepInfo spreadsheet
        end=my_parser(deployment[1]['Date'],deployment[1]['End Time']) ##end time from DepInfo spreadsheet
        end = start+dt.timedelta(minutes=60) ## end time = start time + 1hour
        dep_num = deployment[0]
        #print dep_num,pd.date_range(start,end,freq='1Min')
        deployments=deployments.append(pd.DataFrame(data={'#':dep_num,'start':start,'end':end},index=[dep_num]))  
    deplist = endmembers[by_dep]
    
    SelPoints = pd.DataFrame()
    for dep in deployments.ix[deplist].iterrows(): ## put in Deployment #(s) here
        #print dep[0], dep[1]['start'],dep[1]['end']
        SelPoints= SelPoints.append(AllPoints[dep[1]['start']:dep[1]['end']]) ## [1] gets data from row tuple
        
    AllPoints=SelPoints.sort()


#### Analyze by Gridcell
gridcount=len(shapef.shapes())
AllGridValues=pd.DataFrame()
for shape in shapef.shapes():
    ## get center of shape by finding the mean lat and lon of all points in shapefile polygon
    grid_lons,grid_lats = [],[] # create empty lists for each polygon (grid cell)
    for point in shape.points:
        grid_lons.append(point[0])
        grid_lats.append(point[1])
    grid_lon, grid_lat = np.mean(grid_lons),np.mean(grid_lats) 
    ## get points from the Gridcell
    gridpoints = AllPoints[AllPoints['Gridcell']==gridcount].dropna()
    if len(gridpoints) >= 2:
        #http://python.hydrology-amsterdam.nl/modules/meteolib.py
        ## get mean speed and mean direction by finding mean movement in the x and y directions and finding the bearing
        u=gridpoints['speed m/s'].values    
        D=gridpoints['bearing'].values
    
        ve = 0.0 # define east component of wind speed
        vn = 0.0 # define north component of wind speed
        D = D * math.pi / 180.0 # convert wind direction degrees to radians
        for i in range(0, len(u)):
            ve = ve + u[i] * math.sin(D[i]) # calculate sum east speed components
            vn = vn + u[i] * math.cos(D[i]) # calculate sum north speed components
        ve = - ve / len(u) # determine average east speed component
        vn = - vn / len(u) # determine average north speed component
        uv = math.sqrt(ve * ve + vn * vn) # calculate wind speed vector magnitude
        #Calculate wind speed vector direction
        vdir = scipy.arctan2(ve, vn)
        vdir = vdir * 180.0 / math.pi # Convert radians to degrees
        if vdir < 180:
            Dv = vdir + 180.0
        else:
            if vdir > 180.0:
                Dv = vdir - 180
            else:
                Dv = vdir
        GridMean_speed = uv
        GridMean_bearing=Dv
        GridNumObs = len(gridpoints)
        print 'Mean speed of '+str(GridNumObs)+' points in Gridcell '+str(gridcount)+' = '+'%.2f'%GridMean_speed+' m/s, bearing '+'%.2f'%GridMean_bearing
        GridValues = pd.DataFrame(np.array([[grid_lon,grid_lat,len(gridpoints),GridMean_speed,GridMean_bearing]]),index=[gridcount],columns=['lon','lat','NumObs','speed m/s','bearing'])
        AllGridValues=AllGridValues.append(GridValues)
        #x,y= gMap(grid_lon,grid_lat)
        #plt.text(x,y,'%.0f'%GridMean_bearing,color='w')
    gridcount-=1 # count down from total length of grid by 1  
print 'Max speed for endmember condition: '+by_dep+' '+'%.2f'%AllGridValues['speed m/s'].max()
print 'Min speed for endmember condition: '+by_dep+' '+'%.2f'%AllGridValues['speed m/s'].min()
#    GridMean_speed = gridpoints['speed m/s'].max()
#    GridMean_x = gridpoints['x'].sum()
#    GridMean_y= gridpoints['y'].sum()
#    GridMean_initial_bearing=arctan2(GridMean_x,GridMean_y)
#    GridMean_initial_bearing=degrees(GridMean_initial_bearing)
#    GridMean_bearing= (GridMean_initial_bearing+ 360) % 360
    
#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=False,showBinGrid=True,labelBinGrid=True,showLaunchZones=False)  
from DrifterDataAnalysisTools import plot_mean_grid_velocity
sc=plot_mean_grid_velocity(Map,AllGridValues)
#plot_arrows_by_speed(Map,AllPoints)

#plt.suptitle('End member condition: '+by_dep)

#plt.savefig(figdir+'Velocity gridded/'+'drifters gridded mean velocity-'+by_dep+'.png',transparent=True)
#plt.savefig(figdir+'drifters gridded mean velocity-'+by_dep+'.png',transparent=True)








