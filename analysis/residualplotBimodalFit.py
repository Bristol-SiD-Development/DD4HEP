###############################
# TODO find output plot file name from input file names
# TODO could normalize to any input variable/value
# TODO write output fit parameters to file or add to plot legend?
###############################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ast
from collections import Counter
from scipy.optimize import curve_fit
import click

def evt_duplicates(evtNums):
    seen = set()
    seen_add = seen.add
    # adds all new values to seen and all other to duplicates
    duplicates = set(x for x in evtNums if x in seen or seen_add(x))
    # turn the set into a list
    return list(duplicates)

def calculate_binning(data, nbins, lowestedge, highestedge):

    # Find the bin range
    if min(data) < lowestedge:
        lowestedge = min(data)
        print(f"Changing lowestedge to: {lowestedge}")
    else:
        print("Not changing lowestegde")
    if max(data) > highestedge:
        highestedge = max(data)
        print(f"Changing highestedge to: {highestedge}")
    else:
        print("Not changing highestedge")

    # Set the bin edges
    binEdges = []
    binCentres = []
    binWidth = (highestedge - lowestedge)/nbins
    for binIndex in range(nbins + 1):
        binEdges.append(lowestedge + (binIndex * binWidth))
    for binIndex in binEdges[:-1]:
        binCentres.append(binIndex+(binWidth/2))
    
    return(binEdges, binCentres, binWidth, nbins)

def gaussian(x, *popt):
    A, mu, sigma = popt
    return(A*np.exp(-(x-mu)**2/(2.*sigma**2)))

def bimodal(x, mu1, sigma1, A1, mu2, sigma2, A2):
    return gaussian(x,mu1,sigma1,A1) + gaussian(x,mu2,sigma2,A2)


def clean_dfs(df_CAT, df_SiT):
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

    return(df_CAT, df_SiT, evtsRemovedCounter)


def plot_residual(df_CAT, df_SiT, gun_pT, getters, powersList, p0List):
    
    df_CAT, df_SiT, evtsRemovedCounter = clean_dfs(df_CAT, df_SiT)

    for get, powers, p0s in zip(getters, powersList, p0List):
        powers = ast.literal_eval(powers)
        p0s = ast.literal_eval(p0s)
        for pow, p0 in zip(powers, p0s):

            residual = (df_CAT[get] - df_SiT[get])/(gun_pT**pow)

            print(f"Plotting {get} ** {pow} with p0 {p0}")

            binEdges, binCentres, binWidth, nbins = calculate_binning(residual, 100, 1000, -1000)

            if(residual.empty == False):
                plt.figure(1)
                # Plot hist of residuals
                n, bins, patches = plt.hist(residual, bins=binEdges, log=True, label=f'residual {get}', alpha=0.5)
                
                # Calculate bomodal fit
                popt, pcov = curve_fit(bimodal, binCentres, n, p0)
                print(f'A = {popt[0]} +/- {pcov[0,0]**0.5} mu = {popt[1]} +/- {pcov[1,1]**0.5} sigma = {popt[2]} +/- {pcov[2,2]**0.5}')
                print(f'A = {popt[3]} +/- {pcov[3,3]**0.5} mu = {popt[4]} +/- {pcov[4,4]**0.5} sigma = {popt[5]} +/- {pcov[5,5]**0.5}')
                
                binRange = np.linspace(binEdges[0], binEdges[-1], nbins)
                # Plot the combined distribution...
                plt.plot(binRange, bimodal(binRange, *popt), color='yellow', lw=1, label='model', alpha=1)
                # ...and individual gaussian curves
                plt.plot(binRange, gaussian(binRange, *popt[:3]), color='red', lw=1, ls=":", label='distribution 1')
                plt.plot(binRange, gaussian(binRange, *popt[3:]), color='red', lw=1, ls="--", label='distribution 2')

                plt.legend(loc='upper right')
                plt.xlabel(f'Residual {get}')
                plt.ylabel('Count')
                ax = plt.gca()
                ax.set_ylim((0.08, max(n)+(0.1*max(n))))
                plt.savefig(f'figures/test_residual_2000_{gun_pT}pT_theta20_log_{get}_pT**{pow}.png')
                plt.close()

    print(f"\n### {evtsRemovedCounter} event(s) removed due to multiple or missing tracks\n     {len(df_CAT)} events remain ###\n")
    # (remeber could be less than expected if evts with tracks in n
    return


@click.command()
@click.option('--df_CAT', '-dfCAT', "df_CAT", help='Processed csv containing the CATracks', type=str, prompt=True, multiple=False)
@click.option('--df_SiT', '-dfSiT', "df_SiT", help='Porcessed csv containing the SiTracks', type=str, prompt=True, multiple=False)
@click.option('--gun_pT', '-pT', "gun_pT", help='particle gun transverse momentum', type=int, prompt=True, multiple=False)
@click.option('--getters', '-g', help="variable(s) to plot", type=str, prompt=True, multiple=True)
# -pow MUST be in format [n,n,n]. Use one -pow [n,n,n] for each getter used.
@click.option('--powersList', '-pow', "powersList", help='Power to normalize residual to gun pT by.', type=str, prompt=True, multiple=True)
# -p0 MUST be in list of lists format [[A,mu,sigma,A,mu,sigma],[A,mu,sigma,A,mu,sigma]]. Use one -p0 [[A,mu,sigma,A,mu,sigma]] for each getter used.
# i.e. python3 residualplotWorkingFitsOverlap.py -dfCAT process_2000_100pT_CATracks_theta20.csv -dfSiT process_2000_100pT_SiTracks_theta20.csv -pT 100 -g trkTransmom -pow [2,0] -p0 [[1555,0,0.005,100,0,1],[1555,0,0.005,100,0,1]] -g nHits -pow [2] -p0 [[1555,0,0.005,100,0,1]]
@click.option('--p0', '-p0', "p0List", help='Initial guess for bimodal parameters', type=str, prompt=True, multiple=True)


def main(df_CAT, df_SiT, gun_pT, getters, powersList, p0List):
    df_CAT = pd.read_csv(df_CAT)
    df_SiT = pd.read_csv(df_SiT)

    plot_residual(df_CAT, df_SiT, gun_pT, getters, powersList, p0List)

if __name__=='__main__':
    main()