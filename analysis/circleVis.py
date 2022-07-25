from cProfile import label
from turtle import circle, color
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plotCircle(row):
    omega = row['trkOmega']
    print(omega)
    d0 = row['trkD0']
    phi = row['trkPhi']
    
    R = 1/abs(omega)
    print(R)

    Pxc = ((1/omega)-d0)*np.sin(phi)
    Pyc = -1*((1/omega)-d0)*np.cos(phi)

    print(f'Pxc: {Pxc} Pyc: {Pyc}')

    angle = np.linspace(0, 2*np.pi, 150) 

    x = R*np.cos(angle) + Pxc
    y = R*np.sin(angle) + Pyc

    evt = row['evtNum']
    good = row['goodTrk']

    name = f'Evt {evt} - {good}'

    plt.figure(1)
    plt.plot(x, y, label=name)
    
    return

def calCircle():

    angle = np.linspace(0, 2*np.pi, 150)
    r = 1264 # mm
    x = r*np.cos(angle)
    y = r*np.sin(angle)

    plt.figure(1)
    plt.plot(x, y, label='Calorimeter', color='k')

    return

######################################################
# files = ['fakeTrackRates_2000_2pT_theta88_theta85.csv']
# visEvents = [987]
# files = ['trackDump_1_0_5pT_theta90.csv']
# visEvents = [0]
# files = ['fakeTrackRates_2000_2pT_theta90.csv']
files = ['compare10000_5pT.csv']
visEvents = [44]
######################################################

df_list = []

for f in files:
    # Read & add files as dataframes 
    df = pd.read_csv(f)
    df_list.append(df)

tracksCount = 0

for df in df_list:
    # set up df mask to the events required
    mask = df['evtNum'].isin(visEvents)
    df[mask].apply(plotCircle, axis=1)
    tracksCount += len(df[mask])


# Add calorimeter inner radius as guide
calCircle()

plt.figure(1)
plt.xlim(-1300, 1300)
plt.ylim(-1300, 1300)
ax = plt.gca()
ax.set_aspect(1)
ax.legend(loc='center left', bbox_to_anchor=(0.8, 0.9))
plt.savefig('figures/vis5pT_44.png')
plt.close()