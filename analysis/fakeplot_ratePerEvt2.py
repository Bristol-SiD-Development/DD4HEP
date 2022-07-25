import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LogNorm
import sys

df_list = []
label_list = []

# files = ['fakeTrackRates_2000_pT_theta20.csv', 'fakeTrackRates_2000_pT_theta30.csv', 'fakeTrackRates_2000_pTshort_theta90.csv']
# files = ['fakeTrackRates_2000_pTshort_theta90.csv']
files = ['fakeTrackRates_2000_2pT_theta90.csv', 'fakeTrackRates_2000_3pT_theta90.csv', 'fakeTrackRates_2000_5pT_theta90.csv', 
    'fakeTrackRates_2000_10pT_theta90.csv', 'fakeTrackRates_2000_15pT_theta90.csv', 'fakeTrackRates_2000_25pT_theta90.csv', 
    'fakeTrackRates_2000_35pT_theta90.csv', 'fakeTrackRates_2000_55pT_theta90.csv', 'fakeTrackRates_2000_75pT_theta90.csv',
    'fakeTrackRates_2000_100pT_theta90.csv']
# files = ['fakeTrackRates_2000_2pT_theta90.csv', 'fakeTrackRates_2000_3pT_theta90.csv']

for f in files:
    # Find labels from file names
    suffix = f.split('_')[-1]
    angle = suffix.split('.')[0]
    source = f.split('_')[-2]
    label_list.append(source)

    # Read & add files as dataframes 
    df = pd.read_csv(f)
    df_list.append(df)

getters = ['trkTransmom']


ll_index = 0 # Label List index

gunpTList = []
outerNTracksList = []
outerVarpTList = []
outerMeanTracksList = []
outerVarienceTracksList = []
outerSDTracksList = []
outerMaxNTracksList = []
outerMinNTracksList = []

for df in df_list:
    firstEvtNum = min(df['evtNum'])
    lastEvtNum = max(df['evtNum'])
    
    nTracksList = []

    for evt in range(firstEvtNum, lastEvtNum+1):

        # set up another mask for evt by evt 
        event = (df['evtNum'] == evt)
        eventFake = (df['evtNum'] == evt) & (df['goodTrk'] == False)

        nTracksList.append(len(df[event]))
        outerNTracksList.append(len(df[event]))
        gunpTList.append(int(label_list[ll_index].split('p')[0]))


        if evt % 250 == 0:
            print(f'{evt} events processed')
    
    outerMeanTracksList.append(np.mean(nTracksList))
    outerVarienceTracksList.append(np.var(nTracksList))
    outerSDTracksList.append(np.std(nTracksList))
    outerVarpTList.append(int(label_list[ll_index].split('p')[0]))
    outerMinNTracksList.append(min(nTracksList))
    outerMaxNTracksList.append(max(nTracksList))
    # Reset bin finding params
    lowestedge = 1000
    highestedge = -1000

    # Find the bin range
    if min(nTracksList) < lowestedge:
        lowestedge = min(nTracksList)
        print(f"Changing lowestedge to: {lowestedge}")
    else:
        print("Not changing lowestegde")
    if max(nTracksList) > highestedge:
        highestedge = max(nTracksList)
        print(f"Changing highestedge to: {highestedge}")
    else:
        print("Not changing highestedge")
    
    nbins = highestedge - lowestedge + 1

    # Set the bin edges
    binedges = []
    binCentres = []
    # binwidth = (highestedge - lowestedge)/nbins
    binwidth = 1
    for binIndex in range(nbins + 1):
        binedges.append(lowestedge + (binIndex * binwidth))
    for binIndex in binedges[:-1]:
        binCentres.append(binIndex+(binwidth/2))


    weightings = np.ones_like(nTracksList) / len(nTracksList)

    ll_index += 1

# # plt.xscale('log')
# plt.yscale('log')
# plt.xlabel('n tracks in evt')
# plt.ylabel('occurrence')
# fontP = FontProperties() # Making legend smaller
# fontP.set_size('x-small')
# plt.legend(loc='upper right', prop=fontP)
# # plt.grid(True)
# # cbar = plt.colorbar()
# # cbar.set_label('Frequency')
# plt.title(f'{angle}')
# plt.savefig(f'figures/rate_tracks_per_evt_{get}_{angle}.png')
# plt.close()


# print(f'gunPT: {len(gunpTList)}')
# print(f'outerList: {len(outerNTracksList)}')

# Reset bin finding params
lowestedge = 1000
highestedge = -1000

# Find the bin range
if min(outerNTracksList) < lowestedge:
    lowestedge = min(outerNTracksList)
    print(f"Changing lowestedge to: {lowestedge}")
else:
    print("Not changing lowestegde")
if max(outerNTracksList) > highestedge:
    highestedge = max(outerNTracksList)
    print(f"Changing highestedge to: {highestedge}")
else:
    print("Not changing highestedge")

nbins = highestedge - lowestedge + 1

# Set the bin edges
binedges = []
binCentres = []
# binwidth = (highestedge - lowestedge)/nbins
binwidth = 1
for binIndex in range(nbins + 1):
    binedges.append(lowestedge + (binIndex * binwidth))
for binIndex in binedges[:-1]:
    binCentres.append(binIndex+(binwidth/2))

# plt.figure(3)
# # plt.hist2d(gunpTList, outerNTracksList, bins=[100, 50], cmin=1)
# print(f'gunpTList: {gunpTList}\nouterList: {outerNTracksList}')
# plt.hist2d(gunpTList, outerNTracksList, bins=[100, nbins], cmin=1, norm=LogNorm())
# # plt.xscale('log')
# plt.xlabel('gun pT')
# plt.ylabel('n tracks in evt')
# cbar = plt.colorbar()
# cbar.set_label('Frequency') 
# plt.title(f'{angle}')
# plt.savefig('figures/2dTest.png')
# plt.close()


print(f'outerpTList: {outerVarpTList}\nouterMeanList: {outerMeanTracksList}\nouterSTDList: {outerSDTracksList}')

# plt.figure(4)
# plt.plot(outerVarpTList, outerMeanTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('mean n tracks in evt')
# plt.savefig('figures/meanNtracksTest.png')
# plt.close()

# plt.figure(5)
# plt.plot(outerVarpTList, outerMeanTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('mean n tracks in evt')
# plt.xscale('log')
# plt.savefig('figures/meanNtracksTestlog.png')
# plt.close()

extremeLow = [m - e for m, e in zip(outerMeanTracksList, outerMinNTracksList)]
extremeUpp = [e - m for m , e in zip(outerMeanTracksList, outerMaxNTracksList)]
extremes = [extremeLow, extremeUpp]
plt.figure(4)
plt.errorbar(outerVarpTList, outerMeanTracksList, yerr=outerSDTracksList, fmt='x', ecolor=None, elinewidth=1, capsize=4, capthick=1)
ebExt = plt.errorbar(outerVarpTList, outerMeanTracksList, yerr=extremes, fmt='none', ecolor='r', elinewidth=1, capsize=4, capthick=1, linestyle='--', alpha=0.5)
ebExt[-1][0].set_linestyle('--')
plt.xlabel('gun pT')
plt.ylabel('mean n tracks in evt')
plt.savefig('figures/meanNtracksErrorsTest.png')
plt.close()

# plt.figure(5)
# plt.plot(outerVarpTList, outerMeanTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('mean n tracks in evt')
# plt.xscale('log')
# plt.savefig('figures/meanNtracksTestlog.png')
# plt.close()

# plt.figure(6)
# plt.plot(outerVarpTList, outerVarienceTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('varience n tracks in evt')
# plt.savefig('figures/varienceNtracksTest.png')
# plt.close()

# plt.figure(7)
# plt.plot(outerVarpTList, outerVarienceTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('varience n tracks in evt')
# plt.xscale('log')
# plt.savefig('figures/varienceNtracksTestlog.png')
# plt.close()

# plt.figure(8)
# plt.plot(outerVarpTList, outerSDTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('std n tracks in evt')
# plt.savefig('figures/stdNtracksTest.png')
# plt.close()

# plt.figure(9)
# plt.plot(outerVarpTList, outerSDTracksList, 'x')
# plt.xlabel('gun pT')
# plt.ylabel('std n tracks in evt')
# plt.xscale('log')
# plt.savefig('figures/stdNtracksTestlog.png')
# plt.close()