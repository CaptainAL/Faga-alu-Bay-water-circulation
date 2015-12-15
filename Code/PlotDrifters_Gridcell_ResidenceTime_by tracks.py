# -*- coding: utf-8 -*-
"""
Created on Fri Aug 01 07:48:32 2014

@author: Alex
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy
import gpxpy
import shapefile ## from pyshp
import datetime as dt
from matplotlib.patches import Ellipse, Polygon
from matplotlib.path    import Path

## My functions:
from DrifterDataAnalysisTools import Drifter_Map, speed_and_bearing, speed_and_bearing_to_file, my_parser
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
launch= shapefile.Reader(GISdir+'Launchpads.shp')
#### Build dataset
create_new = False
if create_new==True:
    #AllPoints = speed_and_bearing(tracklist,gridshape=grid,launchzoneshape=launch)
    AllPoints = speed_and_bearing_to_file(dirs,tracklist,gridshape=grid,launchzoneshape=launch)
elif create_new==False:
    AllPoints = pd.DataFrame.from_csv(datadir+'AllPoints.csv') 


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
    
    AllPoints.to_csv(datadir+'AllPoints-'+by_dep+'.csv')


Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=False,showBinGrid=True,labelBinGrid=True,showLaunchZones=False)  


#### Analyze by Gridcell
gridcount=len(grid.shapes()) ##establish grid count

AllMeans=pd.DataFrame()
AllGridValues=pd.DataFrame()

for shape in grid.shapes():
    ## get center of shape by finding the mean lat and lon of all points in shapefile polygon
    grid_lons,grid_lats = [],[] # create empty lists for each polygon (grid cell)
    for point in shape.points:
        grid_lons.append(point[0])
        grid_lats.append(point[1])
    grid_lon, grid_lat = np.mean(grid_lons),np.mean(grid_lats) ## in decimal degrees
    grid_lon, grid_lat = Map(grid_lon,grid_lat,inverse=False) ## in projected degrees
    
    ## get points from the Gridcell
    gridpoints = AllPoints[AllPoints['Gridcell']==gridcount].dropna()
    #print 'Analyzing Gridcell '+str(gridcount)+', '+str(len(gridpoints))+' points'
    if len(gridpoints) >= 4:

        ## Calculate residence time as the average 
        ## time that each drifter track is in grid cell
        residence_times = []
        for i in arange(0,AllPoints['TrackNumber'].max(),dtype=int):
            #print i
            try:
                track_points = gridpoints[gridpoints['TrackNumber'] == i]
                #print len(track_points)
                residence_time = track_points.index[-1] - track_points.index[0]
                #print residence_time
                #print 'Residence time of track '+str(i)+' = '+str(residence_time.seconds/60) +' min'
                ## Append the timedelta in minutes to the list of residence times per track
                residence_times.append(residence_time.seconds/60)
            except:
                pass   
        GridResTime = round(mean(residence_times),1)
            
        #Mean speed/direction
        M=gridpoints['speed m/s'].values    
        D=gridpoints['bearing'].values
    
        ve = 0.0 # define east component of wind speed
        vn = 0.0 # define north component of wind speed
        D = D * math.pi / 180.0 # convert wind direction degrees to radians
        for i in range(0, len(M)):
            ve = ve + M[i] * math.sin(D[i]) # calculate sum east speed components
            vn = vn + M[i] * math.cos(D[i]) # calculate sum north speed components
        ve = - ve / len(M) # determine average east speed component
        vn = - vn / len(M) # determine average north speed component
        u_v = math.sqrt(ve * ve + vn * vn) # calculate wind speed vector magnitude
        
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
        GridMean_speed = u_v
        GridMean_bearing=Dv
        GridNumObs = len(gridpoints)
        
        GridMeanResTime = 100/GridMean_speed/60 ## Time = Distance(m)/Time(m/s) to min /(sec/min)
        print 'Mean speed of '+str(GridNumObs)+' points in Gridcell '+str(gridcount)+' = '+'%.2f'%GridMean_speed+' m/s, bearing '+'%.2f'%GridMean_bearing+', Residence Time= '+'%.2f'%GridResTime+' min'
        grid_lon, grid_lat = np.mean(grid_lons),np.mean(grid_lats) ## in decimal degrees        
        GridValues = pd.DataFrame(np.array([[grid_lon,grid_lat,GridNumObs,GridResTime,GridMeanResTime,GridMean_speed,GridMean_bearing]]),index=[gridcount],columns=['lon','lat','NumObs','ResTime','MeanResTime','speed m/s','bearing'])
        AllGridValues=AllGridValues.append(GridValues)
        
        ## Plot shape
        cMap = mpl.cm.rainbow
        cNorm =  mpl.colors.Normalize(vmin=0,vmax=30) ## = res time?
        m = mpl.cm.ScalarMappable(norm=cNorm,cmap=cMap)
        ResTime_color = m.to_rgba(GridResTime)
        
        verts = np.array(shape.points).T
        poly_lons,poly_lats=Map(verts[0],verts[1])
        xy=zip(poly_lons,poly_lats)
        poly = Polygon(xy,facecolor=ResTime_color,alpha=0.5)
        plt.gca().add_patch(poly)
        
    gridcount-=1 # count down from total length of grid by 1  



from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(Map.ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = mpl.colorbar.ColorbarBase(cax,cmap=cMap,norm=cNorm,orientation='vertical')
cbar.set_label('Residence Time (min)')




#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
from DrifterDataAnalysisTools import plot_arrows_by_speed
#plot_arrows_by_speed(Map,AllPoints)


## Plot mean velocity 
from DrifterDataAnalysisTools import plot_grid_ellipses_arrows
#plot_grid_ellipses_arrows(Map,AllGridValues)

plt.suptitle('End member condition: '+by_dep)

plt.show()



#plt.savefig(figdir+'drifters Res Time-'+by_dep+'.svg',transparent=True)



