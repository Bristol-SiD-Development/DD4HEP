import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import math
import sys
import ast
from collections import Counter, defaultdict

def multi_hits(df):
    nMultiHitLayers = 0
    nMultiHitModules = 0

    x_multiLayer = []
    y_multiLayer = []

    for row in df['hitInfo']:
        hitInfo = ast.literal_eval(row)

        hitDetLay = []
        hitDetLayModSen = []

        for hit in hitInfo:
            hitDetLay.append((hit[2][0], hit[2][2]))
            hitDetLayModSen.append((hit[2][0], hit[2][2], hit[2][3], hit[2][4]))

        if hitDetLay:
            detLayCount = dict(Counter(hitDetLay))
            layVals = detLayCount.values()
            if max(layVals) > 1: # Have multiple hits on a single layer
                detLayModSenCount = dict(Counter(hitDetLayModSen))
                nMultiHitLayers += 1

                # Get the xy positions of hits on layers with multiple hits
                # first find layers with multiple hits
                plotDetLay = []
                for detLay, nHits in zip(detLayCount.keys(), layVals):
                    if nHits > 1:
                        plotDetLay.append(detLay)
                
                # then get the coords from the hitInfo 
                for detLay in plotDetLay:
                    for hit in hitInfo:
                        if (hit[2][0], hit[2][2]) == detLay:
                            x_multiLayer.append(hit[1][0])
                            y_multiLayer.append(hit[1][1])

                # Check for multiple hits on same MODULE/SENSOR
                if max(detLayModSenCount.values()) > 1:
                    nMultiHitModules += 1
                    print(f'\n#### Multi hits module!!!')
                    print(f'detLayModSenCount: {detLayModSenCount}')
                    print(hitInfo, '\n')

    print(f'n multi hits same layer = {nMultiHitLayers}')
    nTrks = len(df)
    print(f'nTrks = {nTrks}')
    print(f'Multi hit layer rate = {nMultiHitLayers/nTrks}')
    print(f'Multi hit module rate = {nMultiHitModules/nTrks}')
    
    return (x_multiLayer, y_multiLayer)

####################################################################
### EDIT ###
# df_CAT = pd.read_csv('layers_procTestCAT.csv')
# df_SiT = pd.read_csv('layers_procTestSiT.csv')
# gun_pT = 2
# # df_CAT = pd.read_csv('loc_2000_2pT_theta90.csv')
# df_SiT = pd.read_csv('loc_2000_2pT_theta90.csv')
# gun_pT = 2
df_CAT = pd.read_csv('process_2000_100pT_CATracks_theta20.csv')
df_SiT = pd.read_csv('process_2000_100pT_SiTracks_theta20.csv')
gun_pT = 100
# df_CAT = pd.read_csv('process_10000_5pT_CATracks_theta90.csv')
# df_SiT = pd.read_csv('process_10000_5pT_SiTracks_theta90.csv')
# gun_pT = 5
####################################################################

print('Looking at CATracks')
x_multiLayer, y_multiLayer = multi_hits(df_CAT)

plt.figure(1)
plt.plot(x_multiLayer, y_multiLayer, 'o', linestyle = '', alpha=0.1, markersize=3)
plt.xlabel('x position (mm)')
plt.ylabel('y position (mm)')
plt.savefig(f'figures/test_multiLayersCAT.png')
plt.xlim(-70, 70)
plt.ylim(-70, 70)
plt.savefig(f'figures/test_multiLayersCAT_zoom.png')
plt.close()

plt.figure(2)
plt.hist2d(x_multiLayer, y_multiLayer, bins=500, norm=LogNorm())
plt.xlabel('x position (mm)')
plt.ylabel('y position (mm)')
cbar = plt.colorbar()
cbar.set_label('Frequency')
plt.savefig(f'figures/test_multiLayersCAT2d.png')
# plt.xlim(-70, 70)
# plt.ylim(-70, 70)
# plt.savefig(f'figures/test_multiLayersCAT2d_zoom.png')
plt.close()

plt.figure(4)
plt.hist2d(x_multiLayer, y_multiLayer, bins=500, norm=LogNorm(), range=[[-70, 70], [-70, 70]])
plt.xlabel('x position (mm)')
plt.ylabel('y position (mm)')
cbar = plt.colorbar()
cbar.set_label('Frequency')
plt.savefig(f'figures/test_multiLayersCAT2d_zoom.png')
plt.close()

print ('\n\nLooking at SiTracks')
x_multiLayer, y_multiLayer = multi_hits(df_SiT)

# plt.figure(3)
# plt.plot(x_multiLayer, y_multiLayer, 'o', linestyle = '', alpha=0.1, markersize=3)
# plt.xlabel('x position (cm)')
# plt.ylabel('y position (cm)')
# plt.savefig(f'figures/test_multiLayersSiT.png')
# plt.close()
