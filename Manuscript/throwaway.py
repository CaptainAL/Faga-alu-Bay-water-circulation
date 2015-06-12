# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 14:10:36 2015

@author: Alex

"""

# Prior work/data
#document.add_paragraph("The only available data on current circulation around Tutuila was found in government and consultant reports, and no data on circulation over the reef flat has been collected (CH2M HILL, 1984; Jacob et al., 2012; Wiles et al., 2012). Militello et al. (2003) modeled wave-induced setup on reef flats and developed stage-frequency relationships for large tropical storms and hurricanes in American Samoa. Thompson and Demirbilek (2002) characterized offshore wave climate from data collected near Western Samoa (1985-1990), and used numerical modeling to simulate wave propagation dynamics in Pago Pago Harbor. ")


## End member definitions
def Endmember_definitions_table():
    XL = pd.ExcelFile(datadir+'Drifter deployment checklist.xlsx')
    endmember_table = XL.parse('EndmemberDefn',header=0,index_col=0,parse_cols='A:D',parse_dates=False)
    endmember_table['End member']=endmember_table.index
    endmember_table = endmember_table[['End member','Year Day 2014', 'Gregorian Day (UTC)','Gregorian Day (Local)']]
    return endmember_table  
Endmember_table = Endmember_definitions_table()
Endmember_table.table_num = str(tab_count())    
## Table: End member definitions
if 'Endmember_table' in locals():
    dataframe_to_table(df=Endmember_table,table_num=Endmember_table.table_num,caption="End member periods",fontsize=9)
    #document.add_paragraph("**Note: Local time is UTC-11 so local dates are actually one day earlier (e.g. Tide=2/18-2/19 Local time)")

### Pics of Bay
Bay_sedplume = {'filename':maindir+'Figures/Pics/Bay clear and plume.png', 'fig_num':str(fig_count())}
## Picture of sediment plume
if 'Bay_sedplume' in locals():
    tables_and_figures.add_picture(Bay_sedplume['filename'],width=Inches(6))
    add_figure_caption(Bay_sedplume['fig_num']," Faga'alu Bay under storm and non-storm conditions. a) Image of the embayment on a typical, rain-free day. The darker areas of the bay are live coral, and the light areas are deeper pools with carbonate sand bottom. b) Image of a flood plume (2/21/14) in the northern portion of the bay following a heavy precipitation event: 51 mm in 2 h. Plumes usually persist for several hours, and rarely are seen after 24h due to the flushing of water through the ava channel and out to sea.") 

Drifters for shallow coral reef environments need to be shallow enough to avoid interaction with corals, deep enough to not be affected by the surface movements, extend high enough to be visible but not high enough to be affected by winds, and finally, rugged enough to sustain the impact of a breaking wave onto the reef in the event it is entrained in the surf zone. 

Vetter (unpublished)  deployed wave/tide gauges in Faga'alu Bay on the southern forereef and reef flat, and an ADCP in the ava , for one year (2012-2013). Vetter (unpublished) concluded flow dynamics in the bay were predominantly forced by waves breaking over the southern reef crest, and the wave influence increased linearly with tide height. Using an estimate of total lagoon volume, Vetter (unpublished) calculated flushing time varied from 2-33 h with wave heights of 0-1.6 m, and mean current speed out of the ava channel was 0.14 m/s.

Imagery-based remote sensing is useful to map the temporal and spatial distribution of flood plume boundaries (Klemas, 2012; Warrick et al., 2007), but even high resolution imagery may not quantify the underlying current circulation, which is a strong control on sediment transport. Instead, 

document.add_paragraph(" Hydrodynamic conditions control sediment accumulation in two ways: by limiting primary deposition, and by resuspending and advecting previously deposited sediment. Following large or intense storm events, sediment-rich freshwater is discharged into reef-fringed bays and advected seaward over the reef by momentum in a thin surface layer. This sediment-rich layer significantly attenuates photosynthetically active radiation and transports fine sediment over the reef where it can settle out of the water column and damage corals. Although the hypopycnal surface plume is able to move counter to prevailing ocean currents (upcurrent) by sliding over denser seawater, as sediment particles settle they are entrained and transported in the prevailing current (Wolanski et al., 2003). As flow velocities increase, residence time of the plume over the reef flat is decreased, limiting time for small particles to settle out of the water column. In reef environments where shallow reef crests limit the propagation of incoming surface wave energy, wave action alone may be insufficient to resuspend and disperse sediment, but in combination with wave- or wind-driven currents, orbital velocities may reach critical shear stress for sediment resuspension and dispersal (Ogston et al., 2004; Hoeke et al., 2013).")


document.add_paragraph("The highest velocity flow was observed over the southernmost part of the reef (AS1) and was oriented predominantly in a northwesterly direction, indicating the strong influence of even small breaking waves over the reef crest. The portion of the reef crest adjacent AS1 receives the most wave energy in Faga'alu, and flow from the reef further to the south of AS1 is open to an even wider window of wave directions from the south and southwest. High speed currents were also measured on the southern reef adjacent to the 'ava at AS2, though not as consisently as at AS1, and predominantly in a southwesterly direction, reflecting the relative orientation of the reef crest. Whereas the flow at AS1 was deflected by the shore, turning the cross-reef flow of water north toward the deeper parts of the bay and the 'ava channel, the flow at AS2 was primarily shoreward into the deep pools in the inshore side of the reef flat. Flow data at AS1 also illustrate the modulating effect of tidal stage on flow speed over the reef flat similar to that observed by Storlazzi et al. (2004) and Presto et al. (2006). During YD 52-55, a decrease in flow speed was observed that coincided with the low tide. As the tide level decreased, less wave energy was able to propagate over the reef crest and friction and turbulence over the reef increases. This effect was observed, but smaller in magnitude, at AS2 because the mean water depth is greater and the height of the corals is less at AS2.")

document.add_paragraph("Flow speeds and direction at AS1 were fairly consistent during all endmember conditions, whereas flow was more variable at AS2 and varied more with increasing wave height. As the wave direction rotated more to the east (Figure "+Forcing_data_timeseries['fig_num']+"), more wave energy was directly incident upon the northern portion of the southern reef. Under tidal influence or offshore winds in the absence of strong waves, there is potential for cross-reef flow directions.  When the waves were larger, the flow speeds at AS2 were higher and oriented predominantly towards shore. Flow velocities were most variable at AS3 on the northern reef, and while flow speed and direction at AS1 and AS2 were predominantly influenced by incident wave conditions, flow at AS3 did not show strong correlation with any of the endmember forcing conditions.")
## explain this better: more wave energy was directly incident upon the northern portion of the southern reef. Under tidal influence or offshore 

document.add_paragraph("Thirty drifter deployments were conducted from January to February 2014, with 22 of those deployments coinciding with the ADCP deployments during YD 47-55 (February 15-23; Table 2). Five drifters were released from the same five launch zones within a 10-m time frame at the beginning of each deployment, and allowed to drift until they exited the offshore end of the ava channel at Pago Pago Harbor (Figure "+Drifter_deployment_table.table_num+"). Five drifters were released from the same five launch zones within a 10-m time frame at the beginning of each deployment, and allowed to drift until they exited the offshore end of the 'ava channel at Pago Pago Harbor (Figure "+Study_Area_map['fig_num']+"). Three general spatial patterns were evident, as shown in Figure "+ALL_Drifter_tracks['fig_num']+": 1) Faster onshore flow speeds (lower residence times) over the southern reef flat; 2) Slower, more variable currents (longer residence times) over the deeper inshore portion of the southern reef flat and inner portion of the embayment that converge on the inshore end of the 'ava channel; and 3) Faster offshore current speeds (lower residence times) over the offshore end of the 'ava channel. Only a few drifters traveled seaward across the reef crest, mainly exiting through a subtle depression in the southern reef crest, and these only occurred at high tide under calm wave and wind conditions. Other anomalous drifter tracks show where drifters were entrained in the surf zone at the reef crest and quickly exited back out to sea in the far northeast portion of the study area.")


Compared to the progressive vectors, the drifter tracks show the spatial heterogeneity of the flow pattern as the water flows over the reef flat, turns parallel to shore and into the ava channel  (Figure "+Progressive_Vectors_ADCP_vs_Drifters['fig_num']+").




document.add_paragraph("Under tidal forcing the drifter tracks over the northern reef were highly erratic, but travel longer distances than under strong onshore winds (Figure "+Progressive_Vectors_ADCP_vs_Drifters['fig_num']+"b). This indicates that under tidal forcing water movement is variable over the reef but strong winds push water into the northwest corner of the embayment, piling up water over the northern reef and increasing residence time. Drifter tracks crossing the reef crest are observed over the southern reef under tidal forcing, in the absence of breaking waves that would strongly force water flow across the reef, preventing seaward flow. Under strong wave conditions (Figure "+Progressive_Vectors_ADCP_vs_Drifters['fig_num']+"e), a more coherent, clockwise flow pattern is observed over both the northern and southern reef as large breaking waves force large amounts of water onto the reef flat, driving flow quickly across the southern reef flat and into the main channel. Despite waves breaking on the the northern reef crest, it appears the flow across the southern reef and into the main channel influences an overall eastward flow over the northern reef and out the main channel (Figure "+Progressive_Vectors_ADCP_vs_Drifters['fig_num']+"e).")


Similar to the progressive vectors, this indicates the current  is more unidirectional at AS1 and AS2, flowing in the direction of the main principal component axis. Currents at AS3 are more variable in direction and lower in magnitude, as indicated by the lower mean flow velocity arrows


document.add_paragraph("Drifter data was spatially binned and EOF's and mean flow velocity were calculated for each 100m x 100m grid cell (Figure "+PCA_gridded['fig_num']+"). Due to their spatial position relative to the flow pattern, some grid cells had a much higher number of observations, especially those grid cells in the middle parts of the bay. More observations suggests more certainty in observed patterns, while some of the outlying grid cells with a small number of observations may have been influenced by an anomalous drifter track. However, the overall pattern of drifter tracks is similar to the results from corresponding Eulerian results: Flow over the southern reef is driven by cross-shore wave-driven transport which flows northward to the main channel. However, while it may be hypothesized that water flows into the main channel and out to sea, the Eulerian data from the ADCPs' suggests all flow is into the bay. Finer resolution drifter data resolves the general counterclockwise flow from the southern reef, over the northern reef and out to sea. The drifter data also illustrates the decreased flow velocity near shore and in the deeper pools on the reef flat. The drifter data also illustrate the increase in flow velocity moving seaward in the main channel. ")

## Gridded velocity by endmembers
document.add_heading('Mean flow speed and direction in 100m gridded cells under Wind, Wave, Calm conditions',level=4)
document.add_paragraph("Drifter data was spatially binned and mean flow velocity was calculated for all drifter tracks under each forcing condition. Over the whole bay, mean flow velocity varied from 1-37 cm/s, 1-36 cm/s, and 5-64 cm/s under tidal, wind, and wave forcing, respectively. Vetter (2013) observed flow speed in the main channel of 1-60 cm/s, with a mean of 14 cm/s. Drifter observations in the gridcell corresponding to Vetter's (2013) ADCP location showed flow speeds of 1-30 cm/s wtih a mean of 8 cm/s, for all forcing conditions. Vetter's (2013) ADCP time series shows lower flow speeds in the channel Jan-April than duriung the more active tradewind season June-October so it is likely that the drifter deployments included more quiescent distribution of days than occur during the whole year. While one large swell event was sampled during the drifter deployments, these conditions appear to be more common during the year than were observed during the one intensive week of drifter deployments. Also, Vetter's (2013) ADCP data sampled the full depth of the water column, as opposed to just the surface current that could be affected by winds, especially when strong east winds blow into the bay. This suggests that perhaps Eulerian and Lagrangian methods are more comparable in shallow depths, where the drifter is influenced by a relatively larger portion of the water column.")

if 'Gridded_Velocity_endmembers' in locals():
    tables_and_figures.add_picture(Gridded_Velocity_endmembers['filename'],width=Inches(6))
    add_figure_caption(Gridded_Velocity_endmembers['fig_num'],caption="Drifter tracks and calculated mean velocity, colored by speed for different forcing conditions. Cells with no drifter observations are left empty.") 
    
    
    