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
background = np.flipud(plt.imread(datadir+'samoa/DRIFTERS/DrifterBackground.png'))
gMap.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])

#### Show Lat/Lon Grid               
#gMap.drawparallels(np.arange(ll[0],ur[0],.001),labels=[1,1,0,0])
#gMap.drawmeridians(np.arange(ll[1],ur[1],.001),labels=[0,0,0,1])

#### Display Shapefiles:
gMap.readshapefile(datadir+'samoa/GIS/fagaalugeo','fagaalugeo') ## Display coastline of watershed
gMap.readshapefile(datadir+'samoa/GIS/DriftersGIS/grid100m_geo','grid100m_geo') ## Display 100m grid cells for statistical analysis
#gMap.readshapefile(datadir+'samoa/GIS/DriftersGIS/Launchpads','Launchpads') ## Display launch zones

#### Read GPX file data of drifter tracks:
gpx = gpxpy.parse(open(datadir+trackdir+'All_Tracks_UTM2S.gpx','r')) ## All tracks
#gpx = gpxpy.parse(open(datadir+trackdir+'Dep1.gpx','r')) ## Single track file
tracklist=gpx.tracks[0:] 
##
ALLgeo = pd.DataFrame() ## create empty dataframes to start
ALLutm = pd.DataFrame()
count=0
for track in tracklist:
    geo_points,utm_points={},{} ## new dictionary per track
    print track.name
    for segment in track.segments:
        for point in segment.points:
            count +=1
            utm_points[point.time]=utm.from_latlon(point.latitude,point.longitude)[0:2] ## utm.py returns the zone as well, just need northing and easting
            geo_points[point.time]=(point.latitude,point.longitude)   ## add lat/lon to dictionary
            
    #### In UTM 2S 
    UTMPoints = pd.DataFrame.from_dict(utm_points,orient='index',dtype=np.float64).sort().resample('1Min')
    UTMPoints.columns=['Y','X']
    UTMPoints['X before']=UTMPoints['X'].shift(1)
    UTMPoints['Y before']=UTMPoints['Y'].shift(1)
    UTMPoints['X after']=UTMPoints['X'].shift(-1)
    UTMPoints['Y after']=UTMPoints['Y'].shift(-1)
    ## Calculate distance by pythagorean theorem
    UTMPoints['distance m'] = ((UTMPoints['X']-UTMPoints['X before'])**2.0 + (UTMPoints['Y after']-UTMPoints['Y before'])**2.0)**0.5
    UTMPoints['speed m/s']= UTMPoints['distance m']/60
    print 'Mean Speed (m/s): '+str(UTMPoints['speed m/s'].mean())
    ALLutm = ALLutm.append(UTMPoints) ## append each track to the whole dataset
    
    #### In Lat/Lon
    GEOPoints = pd.DataFrame.from_dict(geo_points,orient='index',dtype=np.float64).sort().resample('1Min')
    GEOPoints.columns=['lat','lon']
    
    ALLgeo = ALLgeo.append(GEOPoints)
    
    ALLgeo['lon before']=ALLgeo['lon'].shift(1)
    ALLgeo['lat before']=ALLgeo['lat'].shift(1)
    
    ALLgeo['lon after']=ALLgeo['lon'].shift(-1)
    ALLgeo['lat after']=ALLgeo['lat'].shift(-1)
    
    ## To calculate direction in degrees:
    ALLgeo['lat before']=radians(ALLgeo['lat'].shift(1))
    ALLgeo['lat after']=radians(ALLgeo['lat'].shift(-1))
    ALLgeo['diffLong'] = radians(ALLgeo['lon after']-ALLgeo['lon before'])
    ALLgeo['x']=sin(ALLgeo['diffLong']) * cos(ALLgeo['lat after'])
    ALLgeo['y']=cos(ALLgeo['lat before']) * sin(ALLgeo['lat after']) - (sin(ALLgeo['lat before']) * cos(ALLgeo['lat after']) * cos(ALLgeo['diffLong']))
    ALLgeo['initial bearing']=arctan2(ALLgeo['x'],ALLgeo['y'])
    ALLgeo['initial bearing']=degrees(ALLgeo['initial bearing'])
    ALLgeo['bearing']= (ALLgeo['initial bearing']+ 360) % 360

    ## Add speed from UTM calcs above
    ALLgeo['speed m/s'] = ALLutm['speed m/s']

    ## add back in the original lat/lon data (not in radians)
    ALLgeo['lon before']=ALLgeo['lon'].shift(1)
    ALLgeo['lat before']=ALLgeo['lat'].shift(1)
    ALLgeo['lon after']=ALLgeo['lon'].shift(-1)
    ALLgeo['lat after']=ALLgeo['lat'].shift(-1)

#### Plot arrows
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
sc=gMap.quiver(ALLgeo['lon'],ALLgeo['lat'],sin(radians(ALLgeo['bearing'])),cos(radians(ALLgeo['bearing'])),ALLgeo['speed m/s'].values,latlon=True,scale=40,cmap=plt.cm.rainbow) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
  
#### Plot points          
## Plot Points on Basemap: Maps each position point colored by speed
#sc = gMap.scatter(ALLgeo['lon'],ALLgeo['lat'],latlon=True,c=ALLgeo['speed m/s'],cmap=plt.get_cmap('rainbow'))

## Colorbar, scaled to image size
from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar =plt.colorbar(sc, cax=cax)
cbar.set_label('Drifter Speed (m/s)')

## Title
plt.suptitle("ALL Drifter Tracks Faga'alu February-March 2014" )

plt.show()


## Extras:
## Format lat/lon decimal degrees to reasonable accuracy (~1m?)
#Points['lat']=Points['lat'].map(lambda x: '%.9f' % x)
#Points['lon']=Points['lon'].map(lambda x: '%.9f' % x)
#            print str(count)+'({0},{1}) : {2}'.format(point.latitude, point.longitude, point.time)








