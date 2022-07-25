import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import sys
import ast
from collections import Counter

def evt_duplicates(evtNums):
    seen = set()
    seen_add = seen.add
    # adds all new values to seen and all other to duplicates
    duplicates = set(x for x in evtNums if x in seen or seen_add(x))
    # turn the set into a list
    return list(duplicates)

####################################################################
### EDIT ###
df_CAT = pd.read_csv('loc_2000_100pT_CATracks_theta20.csv')
df_SiT = pd.read_csv('loc_2000_100pT_SiTracks_theta20.csv')
gun_pT = 100
# df_CAT = pd.read_csv('loc_2000_2pT_theta90.csv')
# df_SiT = pd.read_csv('loc_2000_2pT_theta90.csv')
# gun_pT = 2
####################################################################

# Working w/ isolated muons so filter out events with != 1 tracks in both CAT and SiT
evtsRemovedCounter = 0
# Filter out evtNums which do not appear (have a track) in either df 
evtRemoveList = set(df_CAT['evtNum']) ^ set(df_SiT['evtNum'])
evtsRemovedCounter += len(evtRemoveList)

# Remove all tracks with this evtNum from both dfs
# First for differences between the dfs
for i in evtRemoveList:
    df_CAT.drop(df_CAT[df_CAT.evtNum == i].index, inplace=True)
    df_SiT.drop(df_SiT[df_SiT.evtNum == i].index, inplace=True)

# Then for remaining evts with > 1 trk
evtRemoveList = evt_duplicates(df_CAT['evtNum'])
evtRemoveList.extend(evt_duplicates(df_SiT['evtNum']))
evtRemoveList = set(evtRemoveList)
evtsRemovedCounter += len(evtRemoveList)

# Remove all tracks with this evtNum from both dfs
# Now for remaining evts w/ multiple tracks
for i in evtRemoveList:
    df_CAT.drop(df_CAT[df_CAT.evtNum == i].index, inplace=True)
    df_SiT.drop(df_SiT[df_SiT.evtNum == i].index, inplace=True)

# Reset indies so can operate on both dfs
df_CAT.reset_index(drop=True, inplace=True)
df_SiT.reset_index(drop=True, inplace=True)

# Calc and add nHits to both dfs
df_CAT['nHits'] = [len(eval(row)) for row in df_CAT['hitInfo']]
df_SiT['nHits'] = [len(eval(row)) for row in df_SiT['hitInfo']]


# getters = ['getD0', 'getPhi', 'getOmega', 'getZ0', 'getTanLambda', 'getChi2', 'getNdf', 'getdEdx', 'getdEdxError', 'getRadiusOfInnermostHit', 'getTransmom', 'getMom', 'nHits']
getters = ['trkTransmom', 'nHits']

for get in getters:
    #    res, res/pT, res/pT**2
    for pow in [0, 1, 2]:

        residual = (df_CAT[get] - df_SiT[get])/(gun_pT**pow)

        # Reset bin finding params
        nbins = 100
        lowestedge = 1000
        highestedge = -1000

        print(f"Plotting {get}")

        # Find the bin range
        if residual.min() < lowestedge:
            lowestedge = residual.min()
            print(f"Changing lowestedge to: {lowestedge}")
        else:
            print("Not changing lowestegde")
        if residual.max() > highestedge:
            highestedge = residual.max()
            print(f"Changing highestedge to: {highestedge}")
        else:
            print("Not changing highestedge")

        # Set the bin edges
        binedges = []
        binwidth = (highestedge - lowestedge)/nbins
        for binIndex in range(nbins + 1):
            binedges.append(lowestedge + (binIndex * binwidth))

        if(residual.empty == False):
            plt.figure(1)
            plt.hist(residual, bins=binedges, log=True, histtype='step', label=f'residual {get}')
            
            plt.legend(loc='upper right')
            # plt.xscale('log')
            plt.xlabel(f'Residual {get}')
            plt.ylabel('Count')
            plt.savefig(f'test_residual_2000_{gun_pT}pT_theta20_log_{get}_pT**{pow}.png')
            plt.close()

print(f"\n### {evtsRemovedCounter} event(s) removed due to multiple or missing tracks\n     {len(df_CAT)} events remain ###\n")
# (remeber could be less than expected if evts with tracks in neither case)
