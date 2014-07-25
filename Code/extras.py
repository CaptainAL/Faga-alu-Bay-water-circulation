# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 10:08:11 2014

@author: Alex
"""

AllPoints = pd.DataFrame() ## create empty dataframes to start
for track in tracklist:
    points={} ## new dictionary per track
#    print 'Track name: '+str(track.name)
    count=0
    for segment in track.segments:
        for point in segment.points:
            count +=1
            if count ==1: ## Test first point in Track to see if its in a Launch zone
                polycount = len(shapef.shapes()) # of polygons in shapefile
                for poly in shapef.shapes(): # loop over polygons in shapefile
                    if point_in_polygon(point.longitude,point.latitude,poly.points)==True: ## Test if point is in polygon
#                        print "point is from polygon "+str(polycount)
                        LaunchZone = polycount ## Set LaunchZone equal to the polygon#
                    else:
                        polycount-=1
                        pass	
                    if polycount==0:
#                        print "Point not in a poygon"
                        LaunchZone=0
            else:  ## pass on the rest of the points     
                pass
            ## Get point data (lat,lon,UTM x, UTM y,LaunchZone)
            points[point.time]=(point.latitude,point.longitude,utm.from_latlon(point.latitude,point.longitude)[0],utm.from_latlon(point.latitude,point.longitude)[1],LaunchZone) ## utm.py returns the zone as well, just need northing and easting
    
    ## Calculates speed and direction per point in each track      
    #### Calcs
    Points = pd.DataFrame.from_dict(points,orient='index',dtype=np.float64).sort().resample('1Min')##if you change resample time you have to change the speed calc below
    Points.columns=['lat','lon','Y','X','LaunchZone']
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



## Extras:
## Format lat/lon decimal degrees to reasonable accuracy (~1m?)
#Points['lat']=Points['lat'].map(lambda x: '%.9f' % x)
#Points['lon']=Points['lon'].map(lambda x: '%.9f' % x)
#            print str(count)+'({0},{1}) : {2}'.format(point.latitude, point.longitude, point.time)



    #### Plot per Track
    #### Plot arrows
    ## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
#    try:    
#        sc=gMap.quiver(Points['lon'],Points['lat'],sin(radians(Points['bearing'])),cos(radians(Points['bearing'])),Points['speed m/s'].values,latlon=True,scale=40,cmap=plt.cm.rainbow) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
#    except:
#        print "Didn't plot "+str(track.name)
#        raise
    #### Plot points          
    ## Plot Points on Basemap: Maps each position point colored by speed
    #sc = gMap.scatter(Points['lon'],Points['lat'],latlon=True,c=Points['speed m/s'],cmap=plt.get_cmap('rainbow'))

#### Plot AllPoints
#### Plot arrows
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)   
#sc=gMap.quiver(AllPoints['lon'].values,AllPoints['lat'].values,sin(radians(AllPoints['bearing'])),cos(radians(AllPoints['bearing'])),AllPoints['speed m/s'].values,latlon=True,scale=40,cmap=plt.cm.rainbow) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by LaunchZone)    
#sc=gMap.quiver(AllPoints['lon'],AllPoints['lat'],sin(radians(AllPoints['bearing'])),cos(radians(AllPoints['bearing'])),AllPoints['Gridcell'].values,latlon=True,scale=40,cmap=plt.cm.Paired,edgecolors='grey',linewidths=0.1) # https://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg22229.html

#### Plot points          
## Plot Points on Basemap: Maps each position point colored by speed
#sc = gMap.scatter(AllPoints['lon'],AllPoints['lat'],latlon=True,c=AllPoints['speed m/s'],cmap=plt.get_cmap('rainbow'))
## Plot Points on Basemap: Maps each position point colored by LaunchZone
#sc = gMap.scatter(AllPoints['lon'],AllPoints['lat'],latlon=True,c=AllPoints['LaunchZone'],cmap=plt.get_cmap('rainbow'))
