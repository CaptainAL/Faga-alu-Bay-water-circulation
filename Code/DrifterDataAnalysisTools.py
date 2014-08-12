# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 06:24:54 2014

@author: Alex
"""
        
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import pandas as pd
import numpy as np
from numpy import sin,cos,radians,arctan2,degrees
import datetime as dt

import gpxpy
import utm
import shapefile ## from pyshp


def my_parser(x,y):#x is the date, y is the time
            y = str(int(y))
            hour=y[:-2]
            minute=y[-2:]
            time=dt.time(int(hour),int(minute))
            parsed=dt.datetime.combine(x,time)
            return parsed
def point_in_polygon(x,y,poly):
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
    
def point_in_gridcell(gridshape,point):
    polycount = len(gridshape.shapes()) # of polygons in shapefile
    for poly in gridshape.shapes(): # loop over polygons in shapefile
        if point_in_polygon(point.longitude,point.latitude,poly.points)==True: ## Test if point is in polygon
            #print "point is from polygon "+str(polycount)
            Gridcell_of_point = polycount ## Set gridcell equal to the polygon#
        else:
            polycount-=1
            pass
    return Gridcell_of_point
    
def point_in_launchzone(launchzoneshape,count,point):
    polycount = len(launchzoneshape.shapes()) # of polygons in shapefile
    for poly in launchzoneshape.shapes(): # loop over polygons in shapefile
        if point_in_polygon(point.longitude,point.latitude,poly.points)==True: ## Test if point is in polygon
#                        print "point is from polygon "+str(polycount)
            LZ = polycount ## Set LaunchZone equal to the polygon#
        else:
            polycount-=1
            pass	
        if polycount==0:
#                        print "Point not in a poygon"
            LZ=0
    return LZ


def bearing(pointA, pointB):
    import math
#"""
#Calculates the bearing between two points.
# 
#The formulae used is the following:
#θ = atan2(sin(Δlong).cos(lat2),
#cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
# 
#:Parameters:
#- `pointA: The tuple representing the latitude/longitude for the
#first point. Latitude and longitude must be in decimal degrees
#- `pointB: The tuple representing the latitude/longitude for the
#second point. Latitude and longitude must be in decimal degrees
# 
#:Returns:
#The bearing in degrees
# 
#:Returns Type:
#float
#"""
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")
 
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
     
    diffLong = math.radians(pointB[1] - pointA[1])
     
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
     
    initial_bearing = math.atan2(x, y)
     
    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
     
    return compass_bearing  

#### from a tracklist of GPS points this constructs a DataFrame
#### with the speed, compass bearing, Launchzone and Grid cell of the point

def speed_and_bearing(tracklist,gridshape=None,launchzoneshape=None):
    AllPoints = pd.DataFrame() ## create empty dataframes to start
    for track in tracklist:
        points={} ## new dictionary per track
        #print 'Track name: '+str(track.name)
        count=0 ## for LaunchZone determination
        for segment in track.segments:
            for point in segment.points:
                ## Determine grid cell of point
                if gridshape==None:
                    Gridcell=np.nan
                elif gridshape!=None:
                    Gridcell = point_in_gridcell(gridshape,point)
                ## Determine Launchzone by testing first point of track 
                if launchzoneshape==None:
                    LaunchZone=np.nan
                elif launchzoneshape!=None:
                    count +=1
                    if count ==1: ## Test first point in Track to see if its in a Launch zone
                        LaunchZone=point_in_launchzone(launchzoneshape,count,point)
                    else:
                        pass
                    
                ## Get point data (lat,lon,UTM x, UTM y,LaunchZone)
                lat,lon = point.latitude,point.longitude
                lat_utm,lon_utm = utm.from_latlon(point.latitude,point.longitude)[0],utm.from_latlon(point.latitude,point.longitude)[1]
                points[point.time]=(lat,lon,lat_utm,lon_utm,Gridcell,LaunchZone) ## utm.py returns the zone as well, just need northing and easting
        
        ## Calculates speed and direction per point in each track      
        #### Calcs
        Points = pd.DataFrame.from_dict(points,orient='index',dtype=np.float64).sort().resample('1Min')##if you change resample time you have to change the speed calc below
        Points.columns=['lat','lon','Y','X','Gridcell','LaunchZone']
        ##
        Points['Gridcell']=Points['Gridcell'].round()
        Points['X before']=Points['X'].shift(1)
        Points['Y before']=Points['Y'].shift(1)
        Points['X after']=Points['X'].shift(-1)
        Points['Y after']=Points['Y'].shift(-1)
        ## Calculate Easting and Northing (m)
        Points['easting']= Points['X before']-Points['X']     
        Points['northing']=Points['Y before']-Points['Y']
        
        ## Calculate distance by pythagorean theorem
        Points['distance m'] = ((Points['X']-Points['X before'])**2.0 + (Points['Y']-Points['Y before'])**2.0)**0.5
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
        AllPoints = AllPoints.sort()
    return AllPoints

def speed_and_bearing_to_file(dirs,tracklist,gridshape=None,launchzoneshape=None):
    AllPoints = speed_and_bearing(tracklist,gridshape,launchzoneshape)
    datadir=dirs['data']
    AllPoints.to_csv(datadir+'AllPoints.csv')
    return AllPoints
#### Make AllPoints csv
#from DrifterDataAnalysisTools import speed_and_bearing_to_file
#launchshapef = shapefile.Reader(GISdir+'Launchpads.shp')
#gridshapef = shapefile.Reader(GISdir+'grid100m_geo.shp')
#AllPoints = speed_and_bearing_to_file(dirs,tracklist,gridshape=gridshapef,launchzoneshape=launchshapef)
    
def Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=True,showBinGrid=True,labelBinGrid=True,showLaunchZones=False):
    figdir=dirs['fig']
    GISdir = dirs['GIS']
    ## Map Extents: Local, Island, Region
    if MapExtent=='Local':
        ll, ur = [-14.294238,-170.683732],[-14.286362, -170.673260] 
        ll, ur = [-14.295337283,-170.684163993],[-14.285531852, -170.673919854]
    elif MapExtent=='Island':
        ll, ur= [-14.4,-170.8], [-14.23, -170.54]
    elif MapExtent=='Region':
        ll, ur = [-20,-177],[-14,-170]
    ## Make Plot
    fig, ax = plt.subplots(1)
    #fig.patch.set_visible(False)
    #ax.axis('off')
    gMap = Basemap(projection='merc', resolution='f',llcrnrlon=ll[1], llcrnrlat=ll[0],urcrnrlon=ur[1], urcrnrlat=ur[0],ax=ax)
    #### Show background image from DriftersBackground.mxd
    if showBackgroundImage==True:
        background = np.flipud(plt.imread(figdir+'DrifterBackgrounds/DrifterBackground_matchCurts.png'))
        gMap.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])
    #### Show Lat/Lon Grid        
    if showLatLonGrid==True:       
        gMap.drawparallels(np.arange(ll[0],ur[0],.001),labels=[1,1,0,0])
        gMap.drawmeridians(np.arange(ll[1],ur[1],.001),labels=[0,0,0,1])
    #### Show Shapefiles:
    if showWatershed==True:
        gMap.readshapefile(GISdir+'fagaalugeo','fagaalugeo') ## Display coastline of watershed
    if showBinGrid==True:
        gMap.readshapefile(GISdir+'grid100m_geo','grid100m_geo',color='w') ## Display 100m grid cells for statistical analysis
    if labelBinGrid==True:
        gridshape=shapefile.Reader(GISdir+'grid100m_geo.shp')
        labelcount=len(gridshape.shapes())
        for shape in gridshape.shapes():
            x,y= gMap(shape.points[0][0],shape.points[0][1])
            plt.text(x,y,labelcount,color='w')
            #print str(labelcount)+' '+str(shape.points[0][0])+' '+str(shape.points[0][1])
            labelcount-=1
    if showLaunchZones==True:
        gMap.readshapefile(GISdir+'Launchpads','Launchpads') ## Display launch zones
        
    return gMap
    
def plot_arrows_by_speed(Map,df):
    sc=Map.quiver(df['lon'].values,df['lat'].values,sin(radians(df['bearing'])),cos(radians(df['bearing'])),df['speed m/s'].values,latlon=True,cmap=plt.cm.rainbow,norm=mpl.colors.Normalize(vmin=0,vmax=0.5),scale=40,pivot='middle',headwidth=5,headlength=5,headaxislength=5,edgecolors='grey',linewidths=0.2) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
    ## Colorbar, scaled to image size
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(Map.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar=plt.colorbar(sc,cax=cax)
    cbar.set_label('Speed m/s')
    plt.show()    
    return sc
    
def label_launch_zones(Map,launchzoneshape):
    #### Label LaunchZones
    labelcount=len(launchzoneshape.shapes())
    label_zones = {1:'4',2:'5',3:'2',4:'1',5:'3'}
    for shape in launchzoneshape.shapes():
        x,y= Map(shape.points[0][0],shape.points[0][1])
        plt.text(x,y,label_zones[labelcount],color='w')
    #    print str(labelcount)+' '+str(shape.points[0][0])+' '+str(shape.points[0][1])
        labelcount-=1
    return
    
def plot_arrows_by_launchzone(Map,df):
    ## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by LaunchZone)    
    sc=Map.quiver(df['lon'].values,df['lat'].values,sin(radians(df['bearing'])),cos(radians(df['bearing'])),df['LaunchZone'].values,latlon=True,scale=30,edgecolors='grey',linewidths=0.1,cmap='rainbow') # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
    ## Colorbar, scaled to image size
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(Map.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar =plt.colorbar(sc, cax=cax)
    cbar.set_label('Launch Zone')
    cbar.set_ticks(range(6))
    plt.show()
    return

def plot_points_by_launchzone(Map,df,colorbar=False):
    sc = Map.scatter(df['lon'].values,df['lat'].values,latlon=True,c=df['LaunchZone'].values,cmap=plt.get_cmap('rainbow'),edgecolor='None') # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
    if colorbar==True:        
        ## Colorbar, scaled to image size
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(Map.ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar =plt.colorbar(sc, cax=cax)
        cbar.set_label('Launch Zone')
        cbar.set_ticks(range(6))
    plt.show()
    return

def label_grid_cells(Map,gridshape):
    labelcount=len(gridshape.shapes())
    for shape in gridshape.shapes():
        x,y= Map(shape.points[0][0],shape.points[0][1])
        plt.text(x,y,labelcount,color='w')
        #print str(labelcount)+' '+str(shape.points[0][0])+' '+str(shape.points[0][1])
        labelcount-=1
    plt.show()
    return
    
def plot_arrows_by_gridcell(Map,df):
    ## Plot direction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by Gridcell)    
    sc=Map.quiver(df['lon'].values,df['lat'].values,sin(radians(df['bearing'])),cos(radians(df['bearing'])),df['Gridcell'].values,latlon=True,scale=30,edgecolors='grey',linewidths=0.1,cmap='rainbow') # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
    ## Colorbar, scaled to image size
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(Map.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar =plt.colorbar(sc, cax=cax)
    cbar.set_label('Grid Cell')
    plt.show()
    return sc
    
def plot_mean_grid_velocity(Map,df):
    Q=Map.quiver(df['lon'].values,df['lat'].values,sin(radians(df['bearing'])),cos(radians(df['bearing'])),df['speed m/s'].values,latlon=True,pivot='middle',edgecolors='k',scale=20,headlength=6,headaxislength=6,linewidths=0.2,cmap=plt.cm.rainbow,norm=mpl.colors.Normalize(vmin=0,vmax=0.3)) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html 
    ## Colorbar, scaled to image size
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(Map.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar=plt.colorbar(Q,cax=cax)
    cbar.set_label('Speed m/s')
    plt.show()  
    return Q
    
def plot_grid_arrows(Map,df):
    Q=Map.quiver(df['lon'].values,df['lat'].values,df['easting'].values,df['northing'].values,df['speed m/s'].values,angles=df['bearing'],latlon=True,pivot='middle',edgecolors='k',scale=2,headlength=1,headaxislength=1,linewidths=0.2,cmap=plt.cm.rainbow,norm=mpl.colors.Normalize(vmin=0,vmax=0.7)) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html    
    ## Colorbar, scaled to image size
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(Map.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar=plt.colorbar(Q,cax=cax)
    cbar.set_label('Speed m/s')
    plt.show()  
    return Q

def plot_grid_ellipses_arrows(Map,df):
    Q=Map.quiver(df['lon'].values,df['lat'].values,sin(radians(df['bearing'])),cos(radians(df['bearing'])),df['speed m/s'].values,latlon=True,edgecolors='k',linewidths=0.2,cmap=plt.cm.rainbow,norm=mpl.colors.Normalize(vmin=0,vmax=0.3)) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html 
    ## Colorbar, scaled to image size
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(Map.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar=plt.colorbar(Q,cax=cax)
    cbar.set_label('Speed m/s')
    plt.show()  
    return Q
    
def princomp(A):
 """ performs principal components analysis 
     (PCA) on the n-by-p data matrix A
     Rows of A correspond to observations, columns to variables. 

 Returns :  
  coeff :
    is a p-by-p matrix, each column containing coefficients 
    for one principal component.
  score : 
    the principal component scores; that is, the representation 
    of A in the principal component space. Rows of SCORE 
    correspond to observations, columns to components.
  latent : 
    a vector containing the eigenvalues 
    of the covariance matrix of A.
 """
 # computing eigenvalues and eigenvectors of covariance matrix
 M = (A-mean(A.T,axis=1)).T # subtract the mean (along columns)
 [eigenValues,eigenVectors] = np.linalg.eig(np.cov(M)) # attention:not always sorted
 score = dot(eigenVectors.T,M) # projection of the data in the new space
 return eigenValues,eigenVectors,score
