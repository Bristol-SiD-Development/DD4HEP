#--------------------------------------------------------------
# clic option file, evt
#
# Issue with label when have same momentum to 3sf
#
# NOTE - face(edge)color/s depends on matplotlib version
#--------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from mpl_toolkits.mplot3d import Axes3D
import ast
import sys

def plotSurfaces():

    angle = np.linspace(0, 2*np.pi, 150)

    # Plot tracker/calorimeter boundary
    r = 1264 # mm, ecal inner radius
    x = r*np.cos(angle)
    y = r*np.sin(angle)
    zpositions = [-1765, 1765] # mm, ecal length
    zvalues = [[zv] * len(x) for zv in zpositions]
    
    lineAngles = np.linspace(0, 2*np.pi, 6)
    linex = r*np.cos(lineAngles)
    liney = r*np.sin(lineAngles)

    plt.figure(1)

    for lx, ly in zip(linex[:-1], liney[:-1]):
        plt.plot([lx, lx], zpositions, [ly, ly], label='Calorimeter', color='k', lw=1, alpha=0.4)

    for z in zvalues:
        # swap y <-> z so y is vertical axis 
        plt.plot(x, z, y, label='Calorimeter', color='k', lw=1, alpha=0.4)


    # Plot tracker layers
    rpositions = np.linspace(217, 1221, 5) # mm, tracker inner, outer radius, 5 layers

    for r in rpositions:
        z = [-1522, 1522] # mm, tracker length
        angle_grid, z_grid=np.meshgrid(angle, z)
        x_grid = r*np.cos(angle_grid)
        y_grid = r*np.sin(angle_grid)

        plt.figure(1)
        surf = ax.plot_surface(x_grid, z_grid, y_grid, label='Tracker', color='k', alpha=0.1)
        surf._edgecolors2d = surf._edgecolors3d
        surf._facecolors2d = surf._facecolors3d

    return

# def plot_hits(row, colour, nTrks):
def plot_hits(row, nTrks):

    #            mu+, e-
    pdgValues = [-13, 11]
    pdgMarkers = ['o', '^']
    pdgMarkerDict = dict(zip(pdgValues, pdgMarkers))

    global i
    # Pick siutable colour map for your situation (search for more as you wish)
    # colours = cm.rainbow(np.linspace(0, 1, nTrks))
    colours = cm.tab10(np.linspace(0, 1, nTrks))
    colour = colours[i]

    good = row['goodTrk']
    if good:
        mkface = colour # default (filled)
    else:
        mkface = 'none' # empty markers

    momentum = round(row['trkMom'], 4) # issue with legend if rounds to same momentum value - need unique for each trk
    hitInfo = ast.literal_eval(row['hitInfo'])
    
    pdgList = []
    xList = []
    yList = []
    zList = []
    markerList = []
    for hitI in hitInfo:
        pdg = hitI[0]
        pdgList.append(pdg)
        x, y, z = hitI[1]
        xList.append(x)
        yList.append(y)
        zList.append(z)
        markerList.append(pdgMarkerDict[pdg])

    plt.figure(1)
    for x, y, z, mk in zip(xList, yList, zList, markerList):
        # swap y <-> z so y is vertical axis 
        ax.plot([x], z, [y], mk, zdir='z', linestyle = '', label=momentum, color=colour, mfc=mkface)
    i += 1
   
    return

######################################################
files = ['loc_10000_5pT_theta90.csv']
# visEvents = [44, 194, 195]
# files = ['loc.csv']
visEvents = [0]
# files = ['loc_2000_2pT_theta90.csv']
# visEvents = [101]
# files = ['loc_100_1pT_theta88.csv']
# visEvents = [5, 6]
# files = ['loc_2000_pT_theta20.csv']
# visEvents = [3410] # e- track
# files = ['loc_2000_pT_theta20.csv']
# visEvents = [0] 
######################################################

df_list = []

for f in files:
    # Read & add files as dataframes 
    df = pd.read_csv(f)
    df_list.append(df)

tracksCount = 0

fig = plt.figure(1)
ax = fig.add_subplot(111, projection='3d')

for df in df_list:
    # set up df mask to the events required
    mask = df['evtNum'].isin(visEvents)

    nT = len(df[mask])
    i = 0
    df[mask].apply(plot_hits, nTrks=nT, axis=1)
    tracksCount += nT


# Add calorimeter inner radius as guide
plotSurfaces()

plt.figure(1)
ax = plt.gca()

handles, labels = ax.get_legend_handles_labels()
# labels will be the keys of the dict, handles will be values
temp = {k:v for k,v in zip(labels, handles)}
ax.legend(temp.values(), temp.keys(), loc='center left', bbox_to_anchor=(0.8, 0.9))
ax.set_xlabel('x')
ax.set_ylabel('z') # recall switch in plotting
ax.set_zlabel('y')
plt.show()
plt.savefig(f'figures/locVisTest.png')
plt.close()




# c1._facecolors2d = c1._facecolors3d
# c1._edgecolors2d = c1._edgecolors3d

# c1._facecolors2d = c1._facecolor3d
# c1._edgecolors2d = c1._edgecolor3d