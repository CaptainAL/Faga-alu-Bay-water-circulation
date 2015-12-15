# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 18:48:27 2015

@author: Alex
"""

# Stokes Law:
#
# http://hinderedsettling.com/2013/08/09/grain-settling-python/
#    
# V = g * D**2 * R  /
#     C1 * visc
#
# g = gravitational acceleration = 9.81 m/s2
# D = particle diameter
# R = (rop - rof) = specific submerged gravity  (the density difference between the particle and fluid, normalized by fluid density)
# rop = particle density (assumed 1 g/cm3)
# rof = medium (seawater) density (assumed 1,025 kg/m3)
# visc = medium (seawater) kinematic viscosity (greek letter nu)
# Kinematic viscosity is the ratio of - absolute (or dynamic) viscosity to density
# 1 Pa s = 1 N s/m2 = 1 kg/(m s)
# 1 poise = 1 dyne s/cm2 = 1 g/(cm s) = 1/10 Pa s = 1/10 N s/m2
# visc_kin = visc_absolute (N s/m2) / fluid density (kg/m3)
# C1 = a constant with a theoretical value of 18


import pandas as pd
import numpy as np
from math import *

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d


rop = 2650.0 # density of particle in kg/m3
rof = 1022.0 # density of water in kg/m3 (35% sal, 29 C) http://www.unisense.com/files/PDF/Diverse/Seawater%20&%20Gases%20table.pdf
## Fresh water
visc = 1.002*1E-3 # dynamic viscosity in Pa*s at 20 C
## Sea water
visc_kin = 8.613*1E-7 # kinematic viscosity N s/m2 (35% sal, 29 C) http://www.unisense.com/files/PDF/Diverse/Seawater%20&%20Gases%20table.pdf
visc_dyn = visc_kin * rof # visc_kin = visc_absolute (N s/m2) / fluid density (kg/m3)
visc = visc_dyn
C1 = 18 # constant in Ferguson-Church equation
C2 = 1 # constant in Ferguson-Church equation
def v_stokes(rop,rof,d,visc,C1):
        R = (rop-rof)/rof # submerged specific gravity
        w = R*9.81*(d**2)/(C1*visc/rof)
        return w
def v_turbulent(rop,rof,d,visc,C2):
        R = (rop-rof)/rof
        w = (4*R*9.81*d/(3*C2))**0.5
        return w
def v_ferg(rop,rof,d,visc,C1,C2):
        R = (rop-rof)/rof
        w = ((R*9.81*d**2)/(C1*visc/rof+
            (0.75*C2*R*9.81*d**3)**0.5))
        return w


d = np.arange(0,0.0005,0.000001)
ws = v_stokes(rop,rof,d,visc,C1)
wt = v_turbulent(rop,rof,d,visc,C2)
wf = v_ferg(rop,rof,d,visc,C1,C2)
figure(figsize=(10,8))
plot(d*1000,ws,label='Stokes',linewidth=3)
plot(d*1000,wt,'g',label='Turbulent',linewidth=3)
plot(d*1000,wf,'r',label='Ferguson-Church',linewidth=3)
plot([0.25, 0.25],[0, 0.15],'k--')
plot([0.25/2, 0.25/2],[0, 0.15],'k--')
plot([0.25/4, 0.25/4],[0, 0.15],'k--')
text(0.36, 0.11, 'medium sand', fontsize=13)
text(0.16, 0.11, 'fine sand', fontsize=13)
text(0.075, 0.11, 'v. fine', fontsize=13)
text(0.08, 0.105, 'sand', fontsize=13)
text(0.01, 0.11, 'silt and', fontsize=13)
text(0.019, 0.105, 'clay', fontsize=13)
legend(loc=2)
xlabel('grain diameter (mm)',fontsize=15)
ylabel('settling velocity (m/s)',fontsize=15)
axis([0,0.5,0,0.15]);
D = [0.068, 0.081, 0.096, 0.115, 0.136, 0.273,
    0.386, 0.55, 0.77, 1.09, 2.18, 4.36]
w = [0.00425, 0.0060, 0.0075, 0.0110, 0.0139, 0.0388,
    0.0551, 0.0729, 0.0930, 0.141, 0.209, 0.307]
scatter(D,w,50,color='k')
show()


d = np.arange(0,0.01,0.00001)
ws = v_stokes(rop,rof,d,visc,C1)
wt = v_turbulent(rop,rof,d,visc,C2)
wf = v_ferg(rop,rof,d,visc,C1,C2)
figure(figsize=(10,8))
loglog(d*1000,ws,label='Stokes',linewidth=3)
loglog(d*1000,wt,'g',label='Turbulent',linewidth=3)
loglog(d*1000,wf,'r',label='Ferguson-Church',linewidth=3)
plot([1.0/64, 1.0/64],[0.00001, 10],'k--')
text(0.012, 0.0007, 'fine silt', fontsize=13,
    rotation='vertical')
plot([1.0/32, 1.0/32],[0.00001, 10],'k--')
text(0.17/8, 0.0007, 'medium silt', fontsize=13,
    rotation='vertical')
plot([1.0/16, 1.0/16],[0.00001, 10],'k--')
text(0.17/4, 0.0007, 'coarse silt', fontsize=13,
    rotation='vertical')
plot([1.0/8, 1.0/8],[0.00001, 10],'k--')
text(0.17/2, 0.001, 'very fine sand', fontsize=13,
    rotation='vertical')
plot([0.25, 0.25],[0.00001, 10],'k--')
text(0.17, 0.001, 'fine sand', fontsize=13,
    rotation='vertical')
plot([0.5, 0.5],[0.00001, 10],'k--')
text(0.33, 0.001, 'medium sand', fontsize=13,
    rotation='vertical')
plot([1, 1],[0.00001, 10],'k--')
text(0.7, 0.001, 'coarse sand', fontsize=13,
    rotation='vertical')
plot([2, 2],[0.00001, 10],'k--')
text(1.3, 0.001, 'very coarse sand', fontsize=13,
    rotation='vertical')
plot([4, 4],[0.00001, 10],'k--')
text(2.7, 0.001, 'granules', fontsize=13,
    rotation='vertical')
text(6, 0.001, 'pebbles', fontsize=13,
    rotation='vertical')
legend(loc=2)
xlabel('grain diameter (mm)', fontsize=15)
ylabel('settling velocity (m/s)', fontsize=15)
axis([0,10,0,10])
scatter(D,w,50,color='k');
show()
    
    
    
    
    
    
    