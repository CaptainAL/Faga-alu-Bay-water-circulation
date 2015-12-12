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

## Statistical Analysis
from scipy import stats

## Plotly
import plotly
import plotly.plotly as py
py.sign_in('CaptainAl', 'xluqsf39yt')

pd.set_option('display.large_repr', 'info')

## Set Directories
git=True
if git==True: ## Git repository
    maindir = 'C:/Users/Alex/Documents/GitHub/Faga-alu-Bay-water-circulation/' 
    datadir=maindir+'Data/'
    trackdir = maindir+'Data/AllTracks/'
    GISdir = maindir+'Data/DriftersGIS/'
    figdir = maindir+'Figures/Figure creation/fromAlex/'
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
##
AllPoints = speed_and_bearing(tracklist)

## Get deployment numbers and time intervals
deployments=pd.DataFrame()
for deployment in DepInfo.iterrows():
    start=my_parser(deployment[1]['Date'],deployment[1]['Start Time'])
    end=my_parser(deployment[1]['Date'],deployment[1]['End Time'])
    dep_num = deployment[1]['Deployment']
    end_mem = deployment.index
    #print dep_num,pd.date_range(start,end,freq='1Min')
    deployments=deployments.append(pd.DataFrame(data={'#':dep_num,'start':start,'end':end,'EndMember':end_mem},index=[dep_num]))
      
#### Plot selections
#Map=Drifter_Map(dirs,MapExtent='Local',showLatLonGrid=False,showBackgroundImage=True,showWatershed=True,showBinGrid=True,showLaunchZones=False)  
#sc=plot_arrows_by_speed(Map,AllPoints)
       
tide=[1,2,3,13,14,15,16,17,18,19,20]    
wind=[4,5,6,7,8,9,10,11,12]
wave=range(21,31)
alldeps=range(1,31)

end_member_dict = {'tide':tide,'wind':wind,'wave':wave}

onebyone = True
if onebyone==True:
    for key in end_member_dict.keys():
        print key
        deplist = end_member_dict[key]
        print deplist
        for dep in deployments.ix[deplist].iterrows(): ## put in Deployment #(s) here
            #Map = Drifter_Plot()
            print dep[0], dep[1]['start'],dep[1]['end']
            if key == 'tide':
                print "getting tide points"
                SelPoints  = AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple
                TidePoints = AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple
            if key == 'wind':
                print "getting wind points"
                SelPoints  = AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple
                WindPoints = AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple 
            if key == 'wave':
                print "getting wave points"
                SelPoints  = AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple
                WavePoints = AllPoints[dep[1]['start']:dep[1]['end']] ## [1] gets data from row tuple
            
            #sc=plot_arrows_by_speed(Map,SelPoints)
        
    
            #plt.suptitle('Deployment: #'+str(dep[0])+' '+str(dep[1]['start'])+'-'+str(dep[1]['end']))
            #plt.savefig(figdir+'drifts/deployment_'+str(dep[0])+'.png')

#plt.show()

## Compile
Speeds = pd.concat([TidePoints['speed m/s'].reset_index()['speed m/s'],WindPoints['speed m/s'].reset_index()['speed m/s'],WavePoints['speed m/s'].reset_index()['speed m/s']],ignore_index=True,axis=1)    
Speeds.columns = ['TIDE','WIND','WAVE']
Speeds['zero'] = 0

## m/s to cm/s
Speeds = Speeds*100

## Parametric
f1,p1 =  stats.f_oneway(Speeds['TIDE'].dropna(),Speeds['WIND'].dropna(),Speeds['WAVE'].dropna())   
print "ANOVA: f = %g  p = %g" % (f1,p1)
TIDE_WIND_ttest1 = stats.ttest_ind(TidePoints['speed m/s'].dropna(), WindPoints['speed m/s'].dropna(), axis=0, equal_var=False)   
print "TIDE v WIND ttest_ind: t = %g  p = %g" % TIDE_WIND_ttest1
TIDE_WAVE_ttest1 = stats.ttest_ind(TidePoints['speed m/s'].dropna(), WavePoints['speed m/s'].dropna(), axis=0, equal_var=False)   
print "TIDE v WAVE ttest_ind: t = %g  p = %g" % TIDE_WAVE_ttest1 
WIND_WAVE_ttest1 = stats.ttest_ind(WindPoints['speed m/s'].dropna(), WavePoints['speed m/s'].dropna(), axis=0, equal_var=False)   
print "WIND v WAVE ttest_ind: t = %g  p = %g" % WIND_WAVE_ttest1 

### Zeros
#f0,p0 =  stats.f_oneway(Speeds['TIDE'].dropna(),Speeds['WIND'].dropna(),Speeds['WAVE'].dropna(),Speeds['zero'])   
#print "ANOVA: f = %g  p = %g" % (f0,p0)
#TIDE_WIND_ttest0 = stats.ttest_ind(Speeds['TIDE'].dropna(),Speeds['zero'], axis=0, equal_var=True)   
#print "TIDE v Zero ttest_ind: t = %g  p = %g" % TIDE_WIND_ttest0
#
#TIDE_WAVE_ttest0 = stats.ttest_ind(Speeds['WAVE'].dropna(),Speeds['zero'], axis=0, equal_var=True)   
#print "WAVE v Zero ttest_ind: t = %g  p = %g" % TIDE_WAVE_ttest0 
#
#WIND_WAVE_ttest0 = stats.ttest_ind(Speeds['WIND'].dropna(),Speeds['zero'], axis=0, equal_var=True)   
#print "WIND v Zero ttest_ind: t = %g  p = %g" % WIND_WAVE_ttest0 


## Non-Parametric
H1, KWp1 = stats.mstats.kruskalwallis(TidePoints['speed m/s'].dropna(),WindPoints['speed m/s'].dropna(),WavePoints['speed m/s'].dropna())
print "Kruskall-Wallis: H = %g  p = %g" % (H1, KWp1) 
TIDE_WIND_mannwhit1 = stats.mannwhitneyu(TidePoints['speed m/s'].dropna(), WindPoints['speed m/s'].dropna())   
print "TIDE v WIND mannwhit: u = %g  p/2 = %g" % TIDE_WIND_mannwhit1
TIDE_WAVE_mannwhit1 = stats.mannwhitneyu(TidePoints['speed m/s'].dropna(),WavePoints['speed m/s'].dropna())   
print "TIDE v WAVE mannwhit: u = %g  p/2 = %g" % TIDE_WAVE_mannwhit1 
WIND_WAVE_mannwhit1 = stats.mannwhitneyu(WindPoints['speed m/s'].dropna(),WavePoints['speed m/s'].dropna())   
print "WIND v WAVE mannwhit: u = %g  p/2 = %g" % WIND_WAVE_mannwhit1 


## PRINT RESULTS
print ''
p = 0.001
print 'p='+str(p)
print 'Parametric statistical tests'

if p1 <= p:
    print "TIDE, WIND, and WAVE are significantly different than each other. ANOVA: f = %.3f  p = %g" % (f1,p1)
elif p1 > p:
    print "TIDE, WIND, and WAVE are NOT significantly different than each other. ANOVA: f = %.3f  p = %g" % (f1,p1)
    
if TIDE_WIND_ttest1[1] <= p:
    print "TIDE and WIND are significantly different than each other. t = %.2f  p = %g" % TIDE_WIND_ttest1
elif TIDE_WIND_ttest1[1] > p:
    print "TIDE and WIND are NOT significantly different than each other. t = %.2f  p = %g" % TIDE_WIND_ttest1
    
if TIDE_WAVE_ttest1[1] <= p:
    print "TIDE and WAVE are significantly different than each other. t = %.2f  p = %g" % TIDE_WAVE_ttest1
elif TIDE_WAVE_ttest1[1] > p:
    print "TIDE and WAVE are NOT significantly different than each other. t = %.2f  p = %g" % TIDE_WAVE_ttest1

if WIND_WAVE_ttest1[1] <= p:
    print "WIND and WAVE are significantly different than each other. t = %.2f  p = %g" % WIND_WAVE_ttest1
elif WIND_WAVE_ttest1[1] > p:
    print "WIND and WAVE are NOT significantly different than each other. t = %.2f  p = %g" % WIND_WAVE_ttest1  
    
#print ''
#print 'Different than Zero'
#
#if p0 <= p:
#    print "TIDE, WIND, and WAVE are significantly different than each other. ANOVA: f = %.3f  p = %g" % (f0,p0)
#elif p0 > p:
#    print "TIDE, WIND, and WAVE are NOT significantly different than each other. ANOVA: f = %.3f  p = %g" % (f0,p0)
#    
#if TIDE_ttest1[1] <= p:
#    print "TIDE and Zero are significantly different than each other. t = %.2f  p = %g" % TIDE_ttest1
#elif TIDE_ttest1[1] > p:
#    print "TIDE and Zero are NOT significantly different than each other. t = %.2f  p = %g" % TIDE_ttest1
#    
#if WIND_ttest1[1] <= p:
#    print "WIND and Zero are significantly different than each other. t = %.2f  p = %g" % WIND_ttest1
#elif WIND_ttest1[1] > p:
#    print "WIND and Zero are NOT significantly different than each other. t = %.2f  p = %g" % WIND_ttest1
#
#if WAVE_ttest1[1] <= p:
#    print "WAVE and Zero are significantly different than each other. t = %.2f  p = %g" % WAVE_ttest1
#elif WAVE_ttest1[1] > p:
#    print "WAVE and Zero are NOT significantly different than each other. t = %.2f  p = %g" % WAVE_ttest1  


print ''
print 'Non-parametric statistical tests'
if KWp1 <= p:
    print "TIDE, WIND, and WAVE are significantly different than each other. Kruskall-Wallis: H = %g  p = %g" % (H1, KWp1) 
elif KWp1 > p:
    print "TIDE, WIND, and WAVE are NOT significantly different than each other. Kruskall-Wallis: H = %g  p = %g" % (H1, KWp1) 
    
if TIDE_WIND_mannwhit1[1] <= p:
    print "TIDE and WIND are significantly different than each other. u = %.2f  p/2 = %g" % TIDE_WIND_mannwhit1
elif TIDE_WIND_mannwhit1[1] > p:
    print "TIDE and WIND are NOT significantly different than each other. u = %.2f  p/2 = %g" % TIDE_WIND_mannwhit1
    
if TIDE_WAVE_mannwhit1[1] <= p:
    print "TIDE and WAVE are significantly different than each other. u = %.2f  p/2 = %g" % TIDE_WAVE_mannwhit1
elif TIDE_WAVE_mannwhit1[1] > p:
    print "TIDE and WAVE are NOT significantly different than each other. u = %.2f  p/2 = %g" % TIDE_WAVE_mannwhit1

if WIND_WAVE_mannwhit1[1] <= p:
    print "WIND and WAVE are significantly different than each other. u = %.2f  p/2 = %g" % WIND_WAVE_mannwhit1
elif WIND_WAVE_mannwhit1[1] > p:
    print "WIND and WAVE are NOT significantly different than each other. u = %.2f  p/2 = %g" % WIND_WAVE_mannwhit1   


print 'Mean speed (STD) for TIDE, WIND, WAVE is '+"%.3f"%Speeds['TIDE'].mean()+' ('+"%.3f"%Speeds['TIDE'].std()+'), '+"%.3f"%Speeds['WIND'].mean()+' ('+"%.3f"%Speeds['WIND'].std()+'), '+"%.3f"%Speeds['WAVE'].mean()+' ('+"%.3f"%Speeds['WAVE'].std()+') cm/s.'





## BOXPLOT and HISTOGRAM
mpl.rc('legend',scatterpoints=1)  
fig, (ax1, ax2) =plt.subplots(2,1,figsize=(8,8))
ax1.text(0.01,0.95,'(a)',verticalalignment='top', horizontalalignment='left',transform=ax1.transAxes,color='k',fontsize=10,fontweight='bold')
ax2.text(0.01,0.95,'(b)',verticalalignment='top', horizontalalignment='left',transform=ax2.transAxes,color='k',fontsize=10,fontweight='bold')     

SpeedsBox = Speeds[['TIDE','WIND','WAVE']]
SpeedsMeans_1 = [Speeds['TIDE'].mean(),Speeds['WIND'].mean(),Speeds['WAVE'].mean()]
SpeedsSTD_1 = [Speeds['TIDE'].std(),Speeds['WIND'].std(),Speeds['WAVE'].std()]
SpeedsVals = np.concatenate([Speeds['TIDE'].dropna().values.tolist(),Speeds['WIND'].dropna().values.tolist(),Speeds['WAVE'].dropna().values.tolist()])
SpeedsCategories = np.concatenate([[1]*len(Speeds['TIDE'].dropna()),[2]*len(Speeds['WIND'].dropna()),[3]*len(Speeds['WAVE'].dropna())])
n_TIDE, n_WIND, n_WAVE = str(len(Speeds['TIDE'].dropna())), str(len(Speeds['WIND'].dropna())), str(len(Speeds['WAVE'].dropna()))
SpeedsBox.columns = ['TIDE: n='+n_TIDE, 'WIND: n='+n_WIND, 'WAVE: n='+n_WAVE]
bp1 = SpeedsBox.boxplot(ax=ax1)
ax1.scatter(SpeedsCategories,SpeedsVals,s=40,marker='+',c='grey',label='speed cm/s')   

## Add Mean values
ax1.scatter([1,2,3],SpeedsMeans_1,s=40,color='k',label='Mean speed (cm/s)')

## Format plots
plt.setp(bp1['boxes'], color='black')
plt.setp(bp1['whiskers'], color='black')
plt.setp(bp1['fliers'], color='grey', marker='+')
plt.setp(bp1['medians'], color='black', marker='+')

log=False
if log==True:
        ax1.set_yscale('log')

ax1.set_ylim(-1,50)
ax1.set_ylabel('cm/s')
ax1.legend(fontsize=10)    

## HISTOGRAM
x0 = Speeds['TIDE'].dropna().values
x1 = Speeds['WIND'].dropna().values
x2 = Speeds['WAVE'].dropna().values

tide = np.ones_like(x0)
tide[:len(x0)/2] = 0.5
wind = np.ones_like(x1)
wind[:len(x1)/2] = 0.5
wave = np.ones_like(x2)
wave[:len(x2)/2] = 0.5

## Line at Mean and Median
ax2.axvline(Speeds['TIDE'].mean(),c='silver',label='TIDE mean:'+"%.1f"%Speeds['TIDE'].mean())
ax2.axvline(Speeds['TIDE'].median(),c='silver',ls='--',label='TIDE median: '+"%.1f"%Speeds['TIDE'].median())
#ax2.text(Speeds['WIND'].mean(),115,'WIND mean: '+"%.3f"%Speeds['WIND'].mean(),rotation=90)
ax2.axvline(Speeds['WIND'].mean(),c='gray',label='WIND mean: '+"%.1f"%Speeds['WIND'].mean())
ax2.axvline(Speeds['WIND'].median(),c='gray',ls='--',label='WIND median: '+"%.1f"%Speeds['WIND'].median())

ax2.axvline(Speeds['WAVE'].mean(),c='k',label='WAVE mean: '+"%.1f"%Speeds['WAVE'].mean())
ax2.axvline(Speeds['WAVE'].median(),c='k',ls='--',label='WAVE median: '+"%.1f"%Speeds['WAVE'].median())


n, bins, patches = ax2.hist( [x0,x1,x2], 10, weights=[tide, wind, wave], histtype='bar',cumulative=False, label=['TIDE', 'WIND', 'WAVE'], color=['silver','gray','k'])
ax2.legend(fontsize=10)

ax2.set_xlabel('cm/s'), ax2.set_ylabel('Number of Observations')


plt.tight_layout(pad=0.01)
plt.savefig(figdir+'End member speed boxplots and histograms')

#plotly_fig = plotly.tools.mpl_to_plotly(fig)



fig, ax2 =plt.subplots(1,1,figsize=(6,4))
## HISTOGRAM
x0 = Speeds['TIDE'].dropna().values
x1 = Speeds['WIND'].dropna().values
x2 = Speeds['WAVE'].dropna().values

tide = np.ones_like(x0)
tide[:len(x0)/2] = 0.5
wind = np.ones_like(x1)
wind[:len(x1)/2] = 0.5
wave = np.ones_like(x2)
wave[:len(x2)/2] = 0.5

## Line at Mean and Median
ax2.axvline(Speeds['TIDE'].mean(),c='silver')#,label='TIDE mean:'+"%.1f"%Speeds['TIDE'].mean())
ax2.axvline(Speeds['TIDE'].median(),c='silver',ls='--')#,label='TIDE median: '+"%.1f"%Speeds['TIDE'].median())
#ax2.text(Speeds['WIND'].mean(),115,'WIND mean: '+"%.3f"%Speeds['WIND'].mean(),rotation=90)
ax2.axvline(Speeds['WIND'].mean(),c='gray')#,label='WIND mean: '+"%.1f"%Speeds['WIND'].mean())
ax2.axvline(Speeds['WIND'].median(),c='gray',ls='--')#,label='WIND median: '+"%.1f"%Speeds['WIND'].median())

ax2.axvline(Speeds['WAVE'].mean(),c='k')#,label='WAVE mean: '+"%.1f"%Speeds['WAVE'].mean())
ax2.axvline(Speeds['WAVE'].median(),c='k',ls='--')#,label='WAVE median: '+"%.1f"%Speeds['WAVE'].median())


n, bins, patches = ax2.hist( [x0,x1,x2], 10, weights=[tide, wind, wave], histtype='bar',cumulative=False, label=['TIDE', 'WIND', 'WAVE'], color=['silver','gray','k'])
ax2.legend(fontsize=10)

ax2.set_xlabel('cm/s'), ax2.set_ylabel('Number of Observations')


plt.tight_layout(pad=0.01)
plt.savefig(figdir+'End member speed histograms.png')
plt.savefig(figdir+'End member speed histograms.pdf')
#plot_url = py.plot_mpl(fig, filename = 'drifters - histogram')