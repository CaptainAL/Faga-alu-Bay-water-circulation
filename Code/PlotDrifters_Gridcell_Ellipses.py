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
import datetime as dt4
from matplotlib.patches import Ellipse

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
Ells = []
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
        uv= gridpoints[['easting','northing']].values
        u, v = gridpoints['easting'].values, gridpoints['northing'].values
        u_avg, v_avg = u.mean(), v.mean()
        ud, vd = u-u_avg, v-v_avg
        
        cov_uv = np.cov(uv.T) ##transpose array
        uv = cov_uv[0,1]
        uu = cov_uv[0,0]
        vv = cov_uv[1,1]
        angle = 0.5*math.atan2(2*uv,uu-vv)
        
        ua = ud*cos(angle)+vd*sin(angle)
        va = vd*cos(angle)-ud*sin(angle)
        
        cov_uva = np.cov([ua,va])
        uva = cov_uva[0,1]
        uua = cov_uva[0,0]
        vva = cov_uva[1,1]
        
        ra, rb = sqrt(uua), sqrt(vva)
        ellipseX = ra*cos(frange(0,2*pi,2*pi/300))*cos(angle)-sin(angle)*rb*sin(frange(0,2*pi,2*pi/300))
        ellipseY = ra*cos(frange(0,2*pi,2*pi/300))*sin(angle)+cos(angle)*rb*sin(frange(0,2*pi,2*pi/300))
        
        Major_x1,Major_x2 = [-sqrt(uua)*cos(angle),sqrt(uua)*cos(angle)] 
        Major_y1,Major_y2 = [-sqrt(uua)*sin(angle),sqrt(uua)*sin(angle)]
        Minor_x1,Minor_x2 = [-sqrt(vva)*cos(pi/2-angle), sqrt(vva)*cos(pi/2-angle)]
        Minor_y1,Minor_y2 = [sqrt(vva)*sin(pi/2-angle),-sqrt(vva)*sin(pi/2-angle)]
        
#        plt.plot(ud,vd,'og')
#        plt.plot(ellipseX,ellipseY,c='k')
#        plt.plot([Major_x1,Major_x2],[Major_y1,Major_y2],c='r')
#        plt.plot([Minor_x1,Minor_x2],[Minor_y1,Minor_y2],c='g')
#        plt.axis('equal')        
        
        XY = np.array([grid_lon,grid_lat])
        Width=((Major_x1-Major_x2)**2.0 + (Major_y1-Major_y2)**2.0)**0.5
        Height=((Minor_x1-Minor_x2)**2.0 + (Minor_y1-Minor_y2)**2.0)**0.5
        Ells.append(Ellipse(xy=XY,width=Width,height=Height,angle=degrees(angle)))

    gridcount-=1 # count down from total length of grid by 1  

#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=False,showBinGrid=True,labelBinGrid=False,showLaunchZones=False)  
from DrifterDataAnalysisTools import plot_grid_ellipses

ax = plt.gca()
for e in Ells:
    ax.add_artist(e)
    e.set_clip_box(ax.bbox)
    e.set_alpha(rand())
    e.set_facecolor(rand(3))
ax.set_xlim(-100,-200)
ax.set_ylim(0,-100)
plt.show()


#plt.suptitle('End member condition: '+by_dep)

#plt.savefig(figdir+'drifters gridded mean velocity-'+by_dep+'.png',transparent=True)



