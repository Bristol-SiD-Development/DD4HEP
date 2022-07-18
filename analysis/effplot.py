import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint
import math
from matplotlib.font_manager import FontProperties
import sys

# df_20 = pd.read_csv('CATracks_2000_pT_theta20.csv')
# df_30 = pd.read_csv('CATracks_2000_pT_theta30.csv')

# List PDG IDs for adding to denominator
acceptMCP_PDG = [-13]
df_list = []
label_list = []
files = ['CATracks_2000_pT_theta20.csv', 'CATracks_2000_pT_theta30.csv', 'CATracks_2000_pTshort_theta90.csv']

for f in files:
    # Find labels from file names
    suffix = f.split('_')[-1]
    source = suffix.split('.')[0]
    label_list.append(source)

    # Read & add files as dataframes 
    df = pd.read_csv(f)
    df_list.append(df)

getters = ['transmomMCP']

for get in getters:
    print(f"Plotting {get}")

    # Reset bin finding params
    nbins = 250
    lowestedge = 1000
    highestedge = -1000

    for df in df_list:
        # setup df masks
        isPrimary = df['pdgMCP'].isin(acceptMCP_PDG)
        hasTrack = np.isfinite(df['trkPurity'])

        # Find the bin range
        if df[isPrimary][get].min() < lowestedge:
            lowestedge = df[isPrimary][get].min()
            print(f"Changing lowestedge to: {lowestedge}")
        else:
            print("Not changing lowestegde")
        if df[isPrimary][get].max() > highestedge:
            highestedge = df[isPrimary][get].max()
            print(f"Changing highestedge to: {highestedge}")
        else:
            print("Not changing highestedge")

    # Set the bin edges
    binedges = []
    binCentres = []
    binwidth = (highestedge - lowestedge)/nbins
    for binIndex in range(nbins + 1):
        binedges.append(lowestedge + (binIndex * binwidth))
    for binIndex in binedges[:-1]:
        binCentres.append(binIndex+(binwidth/2))

    ll_Index = 0
    for df in df_list:
        # if(df[isPrimary][get].empty == False):
        # setup df masks
        # mask = (data['value2'] == 'A') & (data['value'] > 4)
        # isPrimary = (df['pdgMCP'].isin(acceptMCP_PDG)) & (df[get])
        isPrimary = (df['pdgMCP'].isin(acceptMCP_PDG))
        # hasTrack = np.isfinite(df['trkPurity']) & (df['pdgMCP'].isin(acceptMCP_PDG)) & (df[get])
        hasTrack = np.isfinite(df['trkPurity']) & (df['pdgMCP'].isin(acceptMCP_PDG))

        # print(f'df[isPrimary]: {df[isPrimary]}')
        
        plt.figure(1)
        print('Making intiial histograms...')
        nDenom, binsDenom, patchesDenom = plt.hist(df[isPrimary][get], bins=binedges, histtype='step')
        nNumer, binsNumer, patchesNumer = plt.hist(df[hasTrack][get], bins=binedges, histtype='step')
        plt.close()
        print("...Done")
        sumDenom = 0
        sumNumer = 0
        print(f"nDenom: {nDenom}\nnNumer: {nNumer}")
        for x in nDenom:
            sumDenom += x
        for y in nNumer:
            sumNumer += y
        efficiencies = []
        errors_low = []
        errors_upp = []
        print(f"nNumer: {nNumer} nDenom: {nDenom}")
        for num, den in zip(nNumer, nDenom):
            print(f"num: {num} denom: {den}")
            if den == 0:
                bin_eff = np.nan
            else: 
                bin_eff = num/den
            efficiencies.append(bin_eff)
            # Find binomial confidence interval for bin with Clopper-Pearson 'beta' method
            ci_low, ci_upp = proportion_confint(num, den, alpha=0.05, method='beta')
            # Calculate magnitude of error bars relative to CI & efficiency value
            errors_low.append(bin_eff - ci_low)
            errors_upp.append(ci_upp - bin_eff)

        # print(f"{len(efficiencies)} efficiencies: {efficiencies}")
        # print(f"{len(binedges)} binedges: {binedges}\n{len(binsDenom)} binsDenom: {binsDenom}")
        errors = [errors_low, errors_upp]
        plt.figure(2)
        print(f'label: {label_list[ll_Index]}')
        print(f'shapes - binCentres: {np.shape(binCentres)}, efficiencies: {np.shape(efficiencies)}, errors: {np.shape(errors)}')
        plt.errorbar(binCentres, efficiencies, yerr=errors, label=label_list[ll_Index], fmt='.', ecolor=None, elinewidth=1, capsize=4, capthick=1)
        
        ll_Index += 1    
    
    plt.xscale('log')
    plt.xlabel(f'{get}')
    plt.ylabel('Efficiency')
    fontP = FontProperties() # Making legend smaller
    fontP.set_size('x-small')
    plt.legend(loc='lower right', prop=fontP)
    plt.grid(True)
    plt.savefig(f'figures/eff_2000_{get}_theta.png')
    plt.close()
