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
from mpl_toolkits.basemap import Basemap
import utm
import shapefile ## from pyshp
from point_in_poly import point_in_polygon
import math
import scipy
import datetime as dt

pd.set_option('display.large_repr', 'info')
## Set Directories
datadir = 'C:/Users/Alex/Desktop/'
trackdir = 'samoa/DRIFTERS/AllTracks/'

## Open Spreadsheet of deployment data
XL = pd.ExcelFile(datadir+'samoa/DRIFTERS/Drifter deployment checklist.xlsx')
DepInfo =  XL.parse('Table',header=1,parse_cols='B:O',index_col=0)

## Map Extents: Local, Island, Region
ll = [-14.294238,-170.683732] #ll = [-14.4,-170.8] #ll = [-20,-177]
ur = [-14.286362, -170.673260] #ur = [-14.23, -170.54] #ur = [-14,-170]

## Make Plot
fig, ax = plt.subplots(1)
gMap = Basemap(projection='merc', resolution='f',
               llcrnrlon=ll[1], llcrnrlat=ll[0],
               urcrnrlon=ur[1], urcrnrlat=ur[0],ax=ax)
#### Show background image from DriftersBackground.mxd
#background = np.flipud(plt.imread(datadir+'samoa/DRIFTERS/DrifterBackground.png'))
#gMap.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])

#### Show Lat/Lon Grid               
#gMap.drawparallels(np.arange(ll[0],ur[0],.001),labels=[1,1,0,0])
#gMap.drawmeridians(np.arange(ll[1],ur[1],.001),labels=[0,0,0,1])

#### Display Shapefiles:
gMap.readshapefile(datadir+'samoa/GIS/fagaalugeo','fagaalugeo') ## Display coastline of watershed
gMap.readshapefile(datadir+'samoa/GIS/DriftersGIS/grid100m_geo','grid100m_geo') ## Display 100m grid cells for statistical analysis
#gMap.readshapefile(datadir+'samoa/GIS/DriftersGIS/Launchpads','Launchpads') ## Display launch zones

#### Open shapefiles for analysis
shapef = shapefile.Reader(datadir+'samoa/GIS/DriftersGIS/grid100m_geo.shp')
#### Label Gridcells
labelcount=len(shapef.shapes())
for shape in shapef.shapes():
    x,y= gMap(shape.points[0][0],shape.points[0][1])
    #plt.text(x,y,labelcount,color='w')
    #print str(labelcount)+' '+str(shape.points[0][0])+' '+str(shape.points[0][1])
    labelcount-=1

def point_is_in_polygon(point):
    Gridcell = 0
    polycount = len(shapef.shapes()) # of polygons in shapefile
    for poly in shapef.shapes(): # loop over polygons in shapefile
        if point_in_polygon(point['lon'],point['lat'],poly.points)==True: ## Test if point is in polygon
            #print "point is from polygon "+str(polycount)
            Gridcell = int(polycount) ## Set gridcell equal to the polygon#
        else:
            polycount-=1
            pass
    return Gridcell
    
    
#### Read GPX file data of drifter tracks:
gpx = gpxpy.parse(open(datadir+trackdir+'All_Tracks_UTM2S.gpx','r')) ## All tracks
#gpx = gpxpy.parse(open(datadir+trackdir+'Dep1.gpx','r')) ## Single track file
tracklist=gpx.tracks[0:] 
##
AllPoints = pd.DataFrame() ## create empty dataframes to start
for track in tracklist:
    points={} ## new dictionary per track
    #print 'Track name: '+str(track.name)
    count=0
    for segment in track.segments:
        for point in segment.points:
            count +=1
            ## Get point data (lat,lon,UTM x, UTM y,LaunchZone)
            points[point.time]=(point.latitude,point.longitude,utm.from_latlon(point.latitude,point.longitude)[0],utm.from_latlon(point.latitude,point.longitude)[1]) ## utm.py returns the zone as well, just need northing and easting
    
    ## Calculates speed and direction per point in each track      
    #### Calcs
    Points = pd.DataFrame.from_dict(points,orient='index',dtype=np.float64).sort().resample('1Min')##if you change resample time you have to change the speed calc below
    Points.columns=['lat','lon','Y','X']
    Points['Gridcell']=Points.apply(point_is_in_polygon,axis=1)
        
    ##
    Points['X before']=Points['X'].shift(1)
    Points['Y before']=Points['Y'].shift(1)
    Points['X after']=Points['X'].shift(-1)
    Points['Y after']=Points['Y'].shift(-1)
    ## Calculate distance by pythagorean theorem
    Points['distance m'] = ((Points['X']-Points['X before'])**2.0 + (Points['Y after']-Points['Y before'])**2.0)**0.5
    Points['speed m/s']= Points['distance m']/60 ## Speed = Distance/Time (Time is 1Min=60sec **above in .resample(1Min))
    
    Points['lon before']=Points['lon'].shift(1)
    Points['lat before']=Points['lat'].shift(1)
    
    Points['lon after']=Points['lon'].shift(-1)
    Points['lat after']=Points['lat'].shift(-1)
    
    ## To calculate direction in degrees:
    ## change lat/lon to radians for calculating bearing
    ## technique from: https://gist.github.com/jeromer/2005586
    Points['lat before']=radians(Points['lat'].shift(1))
    Points['lat after']=radians(Points['lat'].shift(-1))
    Points['diffLong'] = radians(Points['lon after']-Points['lon before'])
    Points['x']=sin(Points['diffLong']) * cos(Points['lat after'])
    Points['y']=cos(Points['lat before']) * sin(Points['lat after']) - (sin(Points['lat before']) * cos(Points['lat after']) * cos(Points['diffLong']))
    Points['initial bearing']=arctan2(Points['x'],Points['y'])
    Points['initial bearing']=degrees(Points['initial bearing'])
    Points['bearing']= (Points['initial bearing']+ 360) % 360
    ## change lat/lon back to decimal degrees 
    Points['lon before']=Points['lon'].shift(1)
    Points['lat before']=Points['lat'].shift(1)
    Points['lon after']=Points['lon'].shift(-1)
    Points['lat after']=Points['lat'].shift(-1)
    
#    print 'Mean Track Speed (m/s): '+str("%.2f" % Points['speed m/s'].mean())
    AllPoints = AllPoints.append(Points) ## append each track to the whole dataset
    AllPoints =AllPoints.sort()
    #### Plot per Track
    #### Plot arrows
    ## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
#    try:    
#        sc=gMap.quiver(Points['lon'],Points['lat'],sin(radians(Points['bearing'])),cos(radians(Points['bearing'])),Points['speed m/s'].values,latlon=True,scale=40,cmap=plt.cm.rainbow) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
#    except:
#        print "Didn't plot "+str(track.name)
#        pass
    #### Plot points          
    ## Plot Points on Basemap: Maps each position point colored by speed
    #sc = gMap.scatter(Points['lon'],Points['lat'],latlon=True,c=Points['speed m/s'],cmap=plt.get_cmap('rainbow'))

#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
#sc=gMap.quiver(AllPoints['lon'],AllPoints['lat'],sin(radians(AllPoints['bearing'])),cos(radians(AllPoints['bearing'])),AllPoints['speed m/s'].values,latlon=True,scale=40,cmap=plt.cm.rainbow,edgecolors='k',linewidths=0.1) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html

#### Plot arrows by Gridcell
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by Gridcell)    
#sc=gMap.quiver(AllPoints['lon'],AllPoints['lat'],sin(radians(AllPoints['bearing'])),cos(radians(AllPoints['bearing'])),AllPoints['Gridcell'].values,latlon=True,scale=40,cmap=plt.cm.Paired,edgecolors='grey',linewidths=0.1) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
  
#### Plot points          
## Plot Points on Basemap: Maps each position point colored by speed
#sc = gMap.scatter(AllPoints['lon'],AllPoints['lat'],latlon=True,c=AllPoints['speed m/s'],cmap=plt.get_cmap('rainbow'))
  
## Plot Points on Basemap: Maps each position point colored by LaunchZone
#sc = gMap.scatter(AllPoints['lon'],AllPoints['lat'],latlon=True,c=AllPoints['LaunchZone'],cmap=plt.get_cmap('rainbow'))

## Get deployment numbers and time intervals
def my_parser(x,y):
            y = str(int(y))
            hour=y[:-2]
            minute=y[-2:]
            time=dt.time(int(hour),int(minute))
            parsed=dt.datetime.combine(x,time)
            return parsed
deployments=pd.DataFrame()
for deployment in DepInfo.iterrows():
    start=my_parser(deployment[1]['Date'],deployment[1]['Start Time'])
    end=my_parser(deployment[1]['Date'],deployment[1]['End Time'])
    dep_num = deployment[0]
    #print dep_num,pd.date_range(start,end,freq='1Min')
    deployments=deployments.append(pd.DataFrame(data={'#':dep_num,'start':start,'end':end},index=[dep_num]))  
  
wind=[4,5,6,7,8,10,11,12,13,14,15,16]
calm=[1,2,3,9,17,18,19,20,21,22,23,24]
wave=range(25,31)
alldeps=range(1,31)

## Title
plt.suptitle("Wave" )
deplist = wave
SelPoints = pd.DataFrame()
for dep in deployments.ix[deplist].iterrows(): ## put in Deployment #(s) here
    print dep[0], dep[1]['start'],dep[1]['end']
    SelPoints= AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple
  
AllPoints=SelPoints
  
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
        print 'Mean speed of points in Gridcell '+str(gridcount)+' = '+'%.2f'%GridMean_speed+' m/s, bearing '+'%.2f'%GridMean_bearing
        GridValues = pd.DataFrame(np.array([[grid_lon,grid_lat,GridMean_speed,GridMean_bearing]]),index=[gridcount],columns=['lon','lat','speed m/s','bearing'])
        AllGridValues=AllGridValues.append(GridValues)
        x,y= gMap(grid_lon,grid_lat)
        #plt.text(x,y,'%.0f'%GridMean_bearing,color='w')
    gridcount-=1 # count down from total length of grid by 1  

#    GridMean_speed = gridpoints['speed m/s'].max()
#    GridMean_x = gridpoints['x'].sum()
#    GridMean_y= gridpoints['y'].sum()
#    GridMean_initial_bearing=arctan2(GridMean_x,GridMean_y)
#    GridMean_initial_bearing=degrees(GridMean_initial_bearing)
#    GridMean_bearing= (GridMean_initial_bearing+ 360) % 360
    

#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    

sc=gMap.quiver(AllGridValues['lon'].values,AllGridValues['lat'].values,sin(radians(AllGridValues['bearing'])),cos(radians(AllGridValues['bearing'])),AllGridValues['speed m/s'].values,latlon=True,scale=20,pivot='middle',headlength=6,headaxislength=6,edgecolors='k',linewidths=0.2,cmap=plt.cm.rainbow,norm=mpl.colors.Normalize(vmin=0,vmax=0.4)) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html


## Colorbar, scaled to image size
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar =plt.colorbar(sc, cax=cax)
cbar.set_label('Speed (m/s)')



plt.show()


## Extras:
## Format lat/lon decimal degrees to reasonable accuracy (~1m?)
#Points['lat']=Points['lat'].map(lambda x: '%.9f' % x)
#Points['lon']=Points['lon'].map(lambda x: '%.9f' % x)
#            print str(count)+'({0},{1}) : {2}'.format(point.latitude, point.longitude, point.time)








