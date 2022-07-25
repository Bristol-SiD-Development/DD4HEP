from doctest import BLANKLINE_MARKER
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from statsmodels.stats.proportion import proportion_confint
import math
from matplotlib.font_manager import FontProperties
import sys

df_list = []
label_list = []

files = ['fakeTrackRates_2000_pT_theta20.csv', 'fakeTrackRates_2000_pT_theta30.csv', 'fakeTrackRates_2000_pTshort_theta90.csv']
# files = ['fakeTracks_2000_pT_theta20.csv', 'fakeTracks_2000_pT_theta30.csv']
# files = ['rateTest.csv']

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
    nbins = 100
    lowestedge = 1000
    highestedge = -1000

    for df in df_list:
        # set up df masks
        goodTrk = (df['goodTrk'] == True)
        fakeTrk = (df['goodTrk'] == False)

        # Find the bin range
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
        # if highestedge > 120:
        #     highestedge = 120
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
        # set up df masks
        goodTrk = (df['goodTrk'] == True)
        fakeTrk = (df['goodTrk'] == False)

        plt.figure(1)
        print('Making intiial histograms...')
        nGood, binsGood, patchesGood = plt.hist(df[goodTrk][get], bins=binedges, histtype='step')
        nFake, binsFake, patchesFake = plt.hist(df[fakeTrk][get], bins=binedges, histtype='step')
        plt.close()
        print("...Done")

        rates = []
        for fake, good in zip(nFake, nGood):
            if fake+good == 0:
                bin_rate = np.nan
            else:
                bin_rate = fake / (fake+good)
            rates.append(bin_rate)

        plt.figure(2)
        plt.plot(binCentres, rates, 'x', label=label_list[ll_index])

        ll_index += 1

    # plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(f'{get}')
    plt.ylabel('n fakes / (n good + n fakes)')
    fontP = FontProperties() # Making legend smaller
    fontP.set_size('x-small')
    plt.legend(loc='upper right', prop=fontP)
    plt.grid(True)
    plt.savefig(f'figures/rate_fakes_{get}.png')
    plt.close()
