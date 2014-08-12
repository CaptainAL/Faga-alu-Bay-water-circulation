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
from matplotlib.patches import Ellipse
from matplotlib.transforms import Bbox

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
    
    AllPoints.to_csv(datadir+'AllPoints-'+by_dep+'.csv')


Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=False,showWatershed=False,showBinGrid=True,labelBinGrid=False,showLaunchZones=False)  


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
    print 'Analyzing Gridcell '+str(gridcount)+', '+str(len(gridpoints))+' points'
    if len(gridpoints) >= 4:
        rotation = 0 #the angle to rotate the axes counter-clockwise to bring the positive alongshore component into the strike of the coast and
        #positive onshore component 90 degrees clockwise from the positive alongshore orientation if cross-shore and alongshore components are 
        #desired instead of east-west/north-south (if E-W/N-S is desired, use a rotation angle = 0).
        gridpoints['bearing'] = gridpoints['bearing']+rotation
        u = (sin(gridpoints['bearing']*pi/180)*gridpoints['speed m/s']).values # E-W or cross-shore velocity
        v = (cos(gridpoints['bearing']*pi/180)*gridpoints['speed m/s']).values # N-S or alongshore velocity
        
        u_avg, v_avg = u.mean(), v.mean()
        ud, vd = u-u_avg, v-v_avg
        
        cov_uv = np.cov(np.array([ud,vd])) ##transpose array to input to cov
        uv = cov_uv[0,1]
        uu = cov_uv[0,0]
        vv = cov_uv[1,1]
        Angle = 0.5*math.atan2(2*uv,uu-vv)
        
        ua = ud*cos(Angle)+vd*sin(Angle) # component in principal axis direction
        va = vd*cos(Angle)-ud*sin(Angle)
        
        cov_uva = np.cov(np.array([ua,va]))
        uva = cov_uva[0,1]
        uua = cov_uva[0,0]
        vva = cov_uva[1,1]
        
        #Plot ellipse and principal axis
        ra, rb = sqrt(uua), sqrt(vva)
        ellipseX = ra*cos(frange(0,2*pi,2*pi/300))*cos(Angle)-sin(Angle)*rb*sin(frange(0,2*pi,2*pi/300))
        ellipseY = ra*cos(frange(0,2*pi,2*pi/300))*sin(Angle)+cos(Angle)*rb*sin(frange(0,2*pi,2*pi/300))
        
        Major_x1,Major_x2 = [-sqrt(uua)*cos(Angle),sqrt(uua)*cos(Angle)] 
        Major_y1,Major_y2 = [-sqrt(uua)*sin(Angle),sqrt(uua)*sin(Angle)]
        Minor_x1,Minor_x2 = [-sqrt(vva)*cos(pi/2-Angle), sqrt(vva)*cos(pi/2-Angle)]
        Minor_y1,Minor_y2 = [sqrt(vva)*sin(pi/2-Angle),-sqrt(vva)*sin(pi/2-Angle)]
        
      
        # ellipses ...
        #e = Map.ax.add_artist(Ellipse(xy=XY,width=U,height=V,label=str(gridcount),color='r',fill=False,lw=1))  
        scale_factor = 500
        NumObs = len(gridpoints)
        
        cMap,cNorm = mpl.cm.rainbow, mpl.colors.Normalize(vmin=0,vmax=200) ## =Num of observations
        m = mpl.cm.ScalarMappable(norm=cNorm,cmap=cMap)
        ellipse_color = m.to_rgba(NumObs)
        
        #Major axis
        Map.plot([grid_lon+Major_x1*scale_factor,grid_lon+Major_x2*scale_factor],[grid_lat+Major_y1*scale_factor,grid_lat+Major_y2*scale_factor],c=ellipse_color,lw=1)
        #Minor axis        
        Map.plot([grid_lon+Minor_x1*scale_factor,grid_lon+Minor_x2*scale_factor],[grid_lat+Minor_y1*scale_factor,grid_lat+Minor_y2*scale_factor],c=ellipse_color,lw=1)
        #Ellipse        
        Map.plot(grid_lon+ellipseX*scale_factor,grid_lat+ellipseY*scale_factor,c=ellipse_color,lw=1)
        
        
        ##Raw point data (easting/northing)
        scale_factor = 100
        #Map.plot(grid_lon+u*scale_factor,grid_lat+v*scale_factor,'og')
        #Map.plot(grid_lon,grid_lat,'or')
        
        GridMeans = pd.DataFrame(np.array([[grid_lon,grid_lat,u_avg*scale_factor,v_avg*scale_factor,NumObs]]),index=[gridcount],columns=['lon','lat','u','v','NumObs'])
        AllMeans = AllMeans.append(GridMeans)
#        qHndl = Map.quiver(grid_lon,grid_lat,u_avg*scale_factor,v_avg*scale_factor,color=ellipse_color)
        
        
        #Mean speed/direction
        M=gridpoints['speed m/s'].values    
        D=gridpoints['bearing'].values
    
        ve = 0.0 # define east component of wind speed
        vn = 0.0 # define north component of wind speed
        D = D * math.pi / 180.0 # convert wind direction degrees to radians
        for i in range(0, len(M)):
            ve = ve + M[i] * math.sin(D[i]) # calculate sum east speed components
            vn = vn + M[i] * math.cos(D[i]) # calculate sum north speed components
        ve = - ve / len(u) # determine average east speed component
        vn = - vn / len(u) # determine average north speed component
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
        print 'Mean speed of '+str(GridNumObs)+' points in Gridcell '+str(gridcount)+' = '+'%.2f'%GridMean_speed+' m/s, bearing '+'%.2f'%GridMean_bearing
        grid_lon, grid_lat = np.mean(grid_lons),np.mean(grid_lats) ## in decimal degrees        
        GridValues = pd.DataFrame(np.array([[grid_lon,grid_lat,len(gridpoints),GridMean_speed,GridMean_bearing]]),index=[gridcount],columns=['lon','lat','NumObs','speed m/s','bearing'])
        AllGridValues=AllGridValues.append(GridValues)

    gridcount-=1 # count down from total length of grid by 1  

def MeanEllipse_Arrows(Map,df):
    Q =Map.quiver(df['lon'].values,df['lat'].values,df['u'].values,df['v'].values,df['NumObs'].values,cmap=plt.cm.rainbow,norm=cNorm) 
    return Q
qHndl =  MeanEllipse_Arrows(Map,AllMeans)


from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(Map.ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = mpl.colorbar.ColorbarBase(cax,cmap=plt.cm.rainbow,norm=cNorm,orientation='vertical')
cbar.set_label('# observations')

if by_dep=='wave':
    qk = plt.quiverkey(qHndl, 0.6, -0.02,0.1*scale_factor, '0.1 m/s', labelpos='W')


#### Plot arrows by speed
## Plot dirction arrows (lon and lat of where the point is, U and V of arrow vector (use sin and cos of the dirction in radians), color by speed)    
from DrifterDataAnalysisTools import plot_arrows_by_speed
plot_arrows_by_speed(Map,AllPoints)


## Plot mean velocity 
from DrifterDataAnalysisTools import plot_grid_ellipses_arrows
#plot_grid_ellipses_arrows(Map,AllGridValues)

#plt.suptitle('End member condition: '+by_dep)

plt.show()



plt.savefig(figdir+'drifters P axes with arrows-'+by_dep+'.png',transparent=True)



