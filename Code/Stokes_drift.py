# -*- coding: utf-8 -*-
"""
Created on Tue Dec 08 07:29:56 2015

@author: Alex
"""

import pandas as pd
import numpy as np
from math import *

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d




WaveHts = np.arange(0.,0.26,0.01)
WavePers = np.arange(4.,13.,1.)
water_depths = np.arange(0.4,1.4,0.2)

depth = 0.01




df = pd.DataFrame(columns=['Depth','WaveHt','WavePer','U_Stoke'])
count = 1
for water_depth in water_depths:
    for WaveHt in WaveHts:
        for WavePer in WavePers:
            count +=1
            
            ## Nielsen's (1982) method for Wavelength L in shallow water
            ## Nielsen, P. 1982. "Explicit Formulae for Practical Wave Calculations," Coastal Engineering, Vol 6 No. 4, pp 389-398. 
            ## http://chl.erdc.usace.army.mil/library/publications/chetn/pdf/cancelled/cetn-i-17-C.pdf
            WaveLen_deep = 1.56 * WavePer**2
            WaveLen = (2 * pi * water_depth * WaveLen_deep)**0.5 * (1 - (water_depth/WaveLen_deep)) 
            ## Wave speed from http://hyperphysics.phy-astr.gsu.edu/hbase/watwav.html#c3
            WaveSpeed = ( ((9.81 * WaveLen)/(2*pi)) * tanh(2*pi*(water_depth/WaveLen)) )**0.5
            WaveNum = (2*pi) / WaveLen
            
            #pt1 = (pi**2 * WaveHt**2) / WaveLen**2
            #pt2 = WaveSpeed
            #pt3 = (cos(water_depth * (2*WaveNum*(water_depth - depth)))) / (sin(water_depth**2 * (WaveNum * water_depth)))
            
            ## Equations at http://diginole.lib.fsu.edu/cgi/viewcontent.cgi?article=1016&context=uhm
#            U_Stoke_m = ((pi**2 * WaveHt**2)/(WaveLen**2)) * WaveSpeed * ( (cos(water_depth * (2*WaveNum*(water_depth - depth)))) / (sin(water_depth**2 * (WaveNum * water_depth))) )
            ## or
            ## Dietrich (date) Oil Spill Risk Management: Modeling Gulf of Mexico Circulation and Oil Dispersal
            if water_depth <= WaveLen_deep/20.:
                U_Stoke_m = (((pi * WaveHt)/WaveLen)**2) * WaveSpeed * ((cos(water_depth*(2*(water_depth - depth) * ((2*pi)/WaveLen))))/(sin((water_depth**2) * ( (2*pi*water_depth)/WaveLen) )))
            else:
                U_Stoke_m = np.nan
            
            U_Stoke_cm = U_Stoke_m * 100. ## m/sec to cm/sec
            
            print 'Depth: '+str(depth)+' m, Water Depth: '+str(water_depth)+' m , WavePer: '+str(WavePer)+' sec, WaveLen: '+str(WaveLen)+' m, WaveNum: '+str(WaveNum)+' rad/m, WaveHt: '+str(WaveHt)+' m, U_Stoke: '+"%.4f"%(U_Stoke_cm)+' cm/s'
            
            if U_Stoke_cm >= 0:
                df = df.append(pd.DataFrame({'Depth':water_depth,'WaveHt':WaveHt,'WavePer':WavePer,'U_Stoke':U_Stoke_cm},index = [count]))    
            else: 
                df = df.append(pd.DataFrame({'Depth':water_depth,'WaveHt':WaveHt,'WavePer':WavePer,'U_Stoke':np.nan},index = [count]))
df = df.dropna()

   
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(df['WavePer'].values,df['WaveHt'].values,df['U_Stoke'].values,c=df['Depth'],cmap='Blues')
ax.set_ylabel('WaveHt (m)'), ax.set_xlabel('WavePer (sec)'), ax.set_zlabel('U_Stoke (cm/s)')
ax.set_zlim(0.0, df['U_Stoke'].max()), ax.set_ylim(0.0)

cb1 = plt.colorbar(sc)
cb1.ax.set_ylabel('Water depth (m)')
plt.show()  



#
#import plotly.plotly as py
#from plotly.graph_objs import *
#
#trace1 = Scatter3d(x=df['WavePer'].values,y=df['WaveHt'].values,z=df['U_Stoke'].values,marker=dict(size=4))
#data = Data([trace1])
#
#layout = Layout(
#    scene=Scene(
#        xaxis=XAxis(title='Wave Period (sec)'),
#        yaxis=YAxis(title='Wave Height (m)'),
#        zaxis=ZAxis(title='Stokes Drift (cm/sec)')
#    )
#)
#fig = Figure(data=data, layout=layout)
#
#plot_url = py.plot(fig, filename = 'Stokes Drift f(wave_height, wave_period)')
##    
    
    
    
    
    
    