import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import sys

df_list = []
label_list = []

# files = ['fakeTracks_2000_pT_theta20.csv', 'fakeTracks_2000_pT_theta30.csv', 'fakeTracks_2000_pTshort_theta90.csv']
files = ['loc_2000_pT_theta20.csv']

for f in files:
    # Find labels from file names
    suffix = f.split('_')[-1]
    source = suffix.split('.')[0]
    label_list.append(source)

    # Read & add files as dataframes 
    df = pd.read_csv(f)
    df_list.append(df)

getters = ['trkTransmom']

for get in getters:
    print(f"Plotting {get}")

    # Reset bin finding params
    nbins = 250
    lowestedge = 1000
    highestedge = -1000

    for df in df_list:
        # Find the bin range - look over full range for now
        if df[get].min() < lowestedge:
            lowestedge = df[get].min()
            print(f"Changing lowestedge to: {lowestedge}")
        else:
            print("Not changing lowestegde")
        if df[get].max() > highestedge:
            highestedge = df[get].max()
            print(f"Changing highestedge to: {highestedge}")
        else:
            print("Not changing highestedge")
        # if highestedge > 250:
        #     highestedge = 250
        #     print(f'changed highest edge to {highestedge}')

    # Set the bin edges
    binedges = []
    binCentres = []
    binwidth = (highestedge - lowestedge)/nbins
    for binIndex in range(nbins + 1):
        binedges.append(lowestedge + (binIndex * binwidth))
    for binIndex in binedges[:-1]:
        binCentres.append(binIndex+(binwidth/2))

    ll_index = 0
    for df in df_list:

        # mask to only plot fakes
        # recall bins are over full range of the var from above
        fake = (df['goodTrk'] == False)

        plt.figure(1)
        print(f'label: {label_list[ll_index]}')
        plt.hist(df[fake][get], bins=binedges, histtype='step', label=label_list[ll_index])

        ll_index += 1

    # plt.xscale('log')
    plt.xlabel(f'{get}')
    plt.ylabel('N fakes')
    fontP = FontProperties() # Making legend smaller
    fontP.set_size('x-small')
    plt.legend(loc='upper right', prop=fontP)
    plt.grid(True)
    plt.savefig(f'figures/n_fakes_{get}.png')
    plt.close()
