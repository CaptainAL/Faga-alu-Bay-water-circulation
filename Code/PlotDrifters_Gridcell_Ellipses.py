# -*- coding: utf-8 -*-
"""
Created on Fri Aug 01 07:48:32 2014

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
grid = shapefile.Reader(GISdir+'grid100m_geo.shp')
#AllPoints = speed_and_bearing(tracklist,gridshape=shapef)
AllPoints = pd.DataFrame.from_csv(datadir+'AllPoints.csv') ##in PlotDrifters_byLaunchZone.py

## Select deployments, cut to deployment time
endmembers={"wind":range(9,13),"tide":range(13,21),"wave":range(21,31),"all":range(1,31)} ## range are non inclusive
by_dep='wind'## Set to None if you want to show all the data
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
gridcount=len(grid.shapes()) ##establish grid count
AllGridValues=pd.DataFrame()

fig,ax = plt.subplots()
for shape in grid.shapes():
    ## get center of shape by finding the mean lat and lon of all points in shapefile polygon
    grid_lons,grid_lats = [],[] # create empty lists for each polygon (grid cell)
    for point in shape.points:
        grid_lons.append(point[0])
        grid_lats.append(point[1])
    grid_lon, grid_lat = np.mean(grid_lons),np.mean(grid_lats) 
    ## get points from the Gridcell
    gridpoints = AllPoints[AllPoints['Gridcell']==gridcount].dropna()
    if len(gridpoints) >= 2:
        data= gridpoints[['easting','northing']].values
        mu = data.mean(axis=0)
        data = data - mu
        # data = (data - mu)/data.std(axis=0)  # Uncomment this reproduces mlab.PCA results
        eigenvectors, eigenvalues, V = np.linalg.svd(data.T, full_matrices=False)
        projected_data = np.dot(data, eigenvectors)
        sigma = projected_data.std(axis=0).mean()
        print(eigenvectors)
        def annotate(ax, name, start, end):
            arrow = ax.annotate(name,
                                xy=end, xycoords='data',
                                xytext=start, textcoords='data',
                                arrowprops=dict(facecolor='red', width=2.0))
            return arrow

        ax.scatter(gridpoints['easting'],gridpoints['northing'])
        ax.set_aspect('equal')
        for axis in eigenvectors:
            annotate(ax, '', mu, mu + sigma * axis) 


    gridcount-=1 # count down from total length of grid by 1  

#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
#Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=False,showBinGrid=True,labelBinGrid=False,showLaunchZones=False)  
from DrifterDataAnalysisTools import plot_grid_ellipses

plt.show()


#plt.suptitle('End member condition: '+by_dep)

#plt.savefig(figdir+'drifters gridded mean velocity-'+by_dep+'.png',transparent=True)



