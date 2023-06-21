###############################
# TODO restimate p0 fit params from the initial residual histogram
# TODO find output plot file name from input file names
# TODO could normalize to any input variable/value
# TODO write output fit parameters to file or add to plot legend?
# TODO bins calculated multiple times - should test if updated edges before calc new bins
###############################

### NOT much differnt to v1. Allows multiple to be plotted together but this looks messy so likely not useful... 
# Code should also makes single plots fine so more general is good?

# Now plotting as datapoints at binCentres with erros sqr(n points in bin)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ast
from scipy.optimize import curve_fit
import click
from math import log10, floor
from matplotlib.pyplot import cm
from matplotlib.font_manager import FontProperties
import sys

def read_files(files):
    df_list = []
    label_list = []
    angle_list = []

    for f in files:
        # Find labels from file names
        suffix = f.split('_')[-1]
        thetaAngle = suffix.split('.')[0]
        angle = thetaAngle.split('a')[-1]
        angle_list.append(int(angle))
        source = 'θ='+ angle + '°'
        label_list.append(source)

        # Read & add files as dataframes 
        df = pd.read_csv(f)
        df_list.append(df)
    
    return(df_list, label_list, angle_list)

def calculate_binning(data, nbins, lowestedge, highestedge):

    # Find the bin range
    if np.nanmin(data) < lowestedge:
        lowestedge = np.nanmin(data)
        # print(f"Changing lowestedge to: {lowestedge}")
    # else:
    #     # print("Not changing lowestegde")
    if lowestedge < -0.01:
        lowestedge = -0.01
        # print(f'changed lowest edge to {lowestedge}')
    if np.nanmax(data) > highestedge:
        highestedge = np.nanmax(data)
        # print(f"Changing highestedge to: {highestedge}")
    # else:
    #     print("Not changing highestedge")
    if highestedge > 0.01:
        highestedge = 0.01
        # print(f'changed highest edge to {highestedge}') 

    # Set the bin edges
    binEdges = []
    binCentres = []
    binWidth = (highestedge - lowestedge)/nbins
    for binIndex in range(nbins + 1):
        binEdges.append(lowestedge + (binIndex * binWidth))
    for binIndex in binEdges[:-1]:
        binCentres.append(binIndex+(binWidth/2))
    
    return(binEdges, binCentres, binWidth, nbins)

def theta_colour(theta):
    angles = list(range(20, 100, 10))
    colmap = cm.plasma
    colours = [colmap(i) for i in np.linspace(0, 0.9, len(angles))]
    thetaColourDict = dict(zip(angles, colours))
    try:
        colour = thetaColourDict[theta]
    except:
        print('Theta value not be matched for colour finding')
        sys.exit(1)
    return colour

def gaussian(x, *popt):
    A, mu, sigma = popt
    return(A*np.exp(-(x-mu)**2/(2.*sigma**2)))

def bimodal(x, mu1, sigma1, A1, mu2, sigma2, A2):
    return gaussian(x,mu1,sigma1,A1) + gaussian(x,mu2,sigma2,A2)

def round_to_uncertainty(value, uncert):
    unc = round(uncert, -int(floor(log10(abs(uncert)))))
    val = round(value, -int(floor(log10(abs(uncert)))))
    return (val, unc)

def mid_point(x1, x2):
    return x1 + ((x2 - x1)/2)

def geom_mean_point(x1, x2):
    return np.sqrt(x1*x2)

def gun_bins(lowestedge, highestedge, angle):
        # Set the bin edges - N.B. this function needs changing to test compared to previous values
        #  if using multiple dfs. Not atm so left for now.
    binedges = []
    binCentres = []
    # gunP = [0.05, 0.1, 0.5, 1, 2, 3, 5, 10, 15, 25, 35, 55, 75, 100, 125, 250]
    gunP = [1, 2, 3, 5, 10, 15, 25, 35, 55, 75, 100, 125, 250]
    gun_pT = [np.sin(np.deg2rad(angle))*p for p in gunP]
    print(f'gun_pT: {gun_pT}')
    # binwidth = (highestedge - lowestedge)/nbins
    # for binIndex in range(nbins + 1):
    #     binedges.append(lowestedge + (binIndex * binwidth))
    # for binIndex in binedges[:-1]:
    #     binCentres.append(binIndex+(binwidth/2))

    # Match binning to gun momentum
    # binedges.append(lowestedge) # lowedge
    binedges.append(lowestedge) # lowedge
    # take out as low edge if ~=low gun p
    # binedges.append(geom_mean_point(binedges[0], gun_pT[0])) # low side first gunP
    for i in range((len(gun_pT)-1)):
        # if gun_pT[i] > 1:
        binE = geom_mean_point(gun_pT[i], gun_pT[i+1]) # upper edge for each gun_pT (lowedge already in)
        # print(f'binE: {binE}')
        binedges.append(binE)

    # binedges.append(geom_mean_point(gun_pT[-1], highestedge)) # upper for top gunP
    binedges.append(highestedge)

    for i in range((len(binedges)-1)):
        binC = mid_point(binedges[i], binedges[i+1])
        binCentres.append(binC)
    
    return(binedges, binCentres)


def plot_residual(df_list, label_list, angle_list, getters, getTruth, powersList, p0List, outfile):
    # print(f'df_list: {df_list}, label_list: {label_list}')
    print(label_list)
    print(angle_list)
    # outerCentralSigma = []
    # outerFracIn = []
    # gunBinCentreRemove = []

    for get, getTru, powers, p0s in zip(getters, getTruth, powersList, p0List):
        powers = ast.literal_eval(powers)
        p0s = ast.literal_eval(p0s)
        for pow, p0 in zip(powers, p0s):
            ll_Index = 0

            # # Reset bin finding params
            # lowestedge = 1000
            # highestedge = -1000

            for df_CAT in df_list:

                outerCentralSigma = []
                outerFracIn = []
                gunBinCentreRemove = []

                # Set min as 1 GeV as min to reach calorimeter?
                gunBinEdges, gunBinCentres = gun_bins(min(df_CAT['momMCP']), max(df_CAT['momMCP']), angle_list[ll_Index])
                gunBinEdges, gunBinCentres = gun_bins(0.5, max(df_CAT['momMCP']), angle_list[ll_Index])
               
                print(f"gunBinEdges: {gunBinEdges}")
                print(f'gunBinCentres: {gunBinCentres}')


                # Set bin edges here so common across all plots
                # residual = (df_CAT[get] - df_CAT[getTru])/(df_CAT[getTru]**pow)

                print(f"Plotting {get} ** {pow} with p0 {p0}")

                # binEdges, binCentres, binWidth, nbins = calculate_binning(residual, 350, lowestedge, highestedge)
                # binEdges, binCentres, binWidth, nbins = calculate_binning(residual, 100, lowestedge, highestedge)
                # get current edges for next df
                # lowestedge = binEdges[0]
                # highestedge = binEdges[-1]
                
                # setup masks to split by gunP
                for gunLow, gunHigh, gunBinC in zip(gunBinEdges, gunBinEdges[1:], gunBinCentres):
                    print(f'\nLooking in bin centred at {gunBinC}')
                    momBin = (df_CAT['momMCP'] >= gunLow) & (df_CAT['momMCP'] < gunHigh)

                    residual = (df_CAT[momBin][get] - df_CAT[momBin][getTru])/(df_CAT[momBin][getTru]**pow)
                    residual = residual.dropna()
                    # print(f'\nlen: {len(residual)}')

                    if len(residual) < 20:
                        print('Insufficient tracks - Passing')
                        gunBinCentreRemove.append(gunBinC)
                        continue

                    # Reset bin finding params
                    lowestedge = 1000
                    highestedge = -1000
                    
                    # meanRes = np.mean(residual)
                    # stdRes = np.std(residual)
                    # print(f'meanRes: {meanRes}, stdRes: {stdRes}')
                    # sys.exit()
                    binEdges, binCentres, binWidth, nbins = calculate_binning(residual, 250, lowestedge, highestedge)
                    # binEdges, binCentres, binWidth, nbins = calculate_binning(residual, 250, meanRes-5*stdRes, meanRes+5*stdRes)
                    # binEdges, binCentres, binWidth, nbins = calculate_binning(residual, 100, lowestedge, highestedge)
                    # get current edges for next df
                    lowestedge = binEdges[0]
                    highestedge = binEdges[-1]

                    # print(f'df 1 \n{df_CAT[momBin][getTru]}')
                    # print(f'residual1: {residual}\len: {len(residual)}')
                    # residual = residual.dropna()
                    # print(f'\nnot null: {residual}\nlen: {len(residual)}')
                    # print(f'\nlen: {len(residual)}')
                    # sys.exit()

                    
                    plt.figure(2)
                    heights, bins, patches = plt.hist(residual, bins=binEdges, log=True, histtype='step')
                    # plt.xlim(-1, 1)
                    # plt.show()
                    plt.close()
                    # print(heights)
                    # sys.exit()

                    ## could be useful...?
                    # for i in range(len(heights)):
                    #     if heights[i] <= 2:
                    #         # heights[i] = np.nan
                    #         heights[i] = 0
                    #         # print('low bin set nan')
                    #         # lowBinCounter += 1
                    #         bins[i] = np.nan

                    # Get sum of heights to normalise to unity
                    sumHeights = np.sum(heights)
                    # print(sumHeights)
                    normHeights = [h/sumHeights for h in heights]

                    # plt.figure(1)
                    # # Plot value of residuals at bin centre, uncertainties sqrt(n) in bin
                    # pointErrs = [np.sqrt(h)/sumHeights for h in heights]
                    # # print(pointErrs)
                    # plt.errorbar(binCentres, normHeights, yerr=pointErrs, fmt='xk', alpha=0.8, markersize=3.75, elinewidth=1, capsize=2, capthick=1, label=label_list[ll_Index])
                    # plt.show()
                    # sys.exit()
                    # Calculate bomodal fit
                    # popt, pcov = curve_fit(bimodal, binCentres, normHeights, p0, maxfev=5000)
                    # if gunBinC < 1: 
                    #     p0 = [0.5, 0, 0.02]
                    popt, pcov = curve_fit(gaussian, binCentres, normHeights, p0, maxfev=5000)
                    # print(popt)
                    # print(pcov)
                    # a = np.isinf(pcov[0][0])
                    # print(a)
                    if np.isinf(pcov[0][0]):
                        print('Could not conoverge - Passing' )
                        gunBinCentreRemove.append(gunBinC)
                        continue
                        
                    # sys.exit()
                    # modelA = popt[0] + popt[3]
                    fitInfo1 = f'A = {round_to_uncertainty(popt[0], pcov[0,0]**0.5)[0]} \u00B1 {round_to_uncertainty(pcov[0,0]**0.5, pcov[0,0]**0.5)[1]}\nμ = {round_to_uncertainty(popt[1], pcov[1,1]**0.5)[0]} \u00B1 {round_to_uncertainty(pcov[1,1]**0.5, pcov[1,1]**0.5)[1]}\nσ = {round_to_uncertainty(popt[2], pcov[2,2]**0.5)[0]} \u00B1 {round_to_uncertainty(pcov[2,2]**0.5, pcov[2,2]**0.5)[1]}'
                    # print(fitInfo1)
                    # fitInfo2 = f'A = {round_to_uncertainty(popt[3], pcov[3,3]**0.5)[0]} \u00B1 {round_to_uncertainty(pcov[3,3]**0.5, pcov[3,3]**0.5)[1]}\nμ = {round_to_uncertainty(popt[4], pcov[4,4]**0.5)[0]} \u00B1 {round_to_uncertainty(pcov[4,4]**0.5, pcov[4,4]**0.5)[1]}\nσ = {round_to_uncertainty(popt[5], pcov[5,5]**0.5)[0]} \u00B1 {round_to_uncertainty(pcov[5,5]**0.5, pcov[5,5]**0.5)[1]}'
                    # print(fitInfo2)

                    # Add to outer lists
                    if round_to_uncertainty(popt[0], pcov[0,0]**0.5)[0] < 0.01:
                        print(f'!!!! Low A - possibly bad fit\n{fitInfo1}')
                    outerCentralSigma.append(round_to_uncertainty(popt[2], pcov[2,2]**0.5)[0])
                    # A*sqrt(2pi)*sigma
                    outerFracIn.append((round_to_uncertainty(popt[0], pcov[0,0]**0.5)[0]*np.sqrt(2*np.pi)*round_to_uncertainty(popt[2], pcov[2,2]**0.5)[0]))

                    # sys.exit()
                    # binRange = np.linspace(binEdges[0], binEdges[-1], nbins)
                    # # Plot the combined distribution...
                    # plt.plot(binRange, bimodal(binRange, *popt), color='yellow', lw=1, label='Combined', alpha=1)
                    # # ...and individual gaussian curves
                    # # (swapped order so appear correctly in legend)
                    # plt.plot(binRange, gaussian(binRange, *popt[3:]), color='red', lw=1, ls="--", label=fitInfo2, alpha=1)
                    # plt.plot(binRange, gaussian(binRange, *popt[:3]), color='red', lw=1, ls=":", label=fitInfo1, alpha=1)
                    # ll_Index += 1

            # ax = plt.gca()
            # handles, labels = ax.get_legend_handles_labels()
            # ax.legend(handles[::-1], labels[::-1], loc='upper right')
            # # plt.legend(loc='upper right')
            # ### EDIT
            # plt.xlabel(r'$Δp_{T}/p_{T}^{2}$ (GeV$^{-1}$)')
            # plt.ylabel('Normalised count')
            # plt.yscale('log')
            # ### EDIT
            # plt.xlim(-15, 15)
            # # plt.xlim(-2, 2)
            # # plt.xlim(-1, 1)
            # plt.ylim(10**-5, 1)
            # saveFile = outfile
            # saveFile += f'{get}**{pow}.png'
            # plt.savefig(f'{saveFile}')
            # plt.close()
            
                gunBinC_plotting = [p for p in gunBinCentres if p not in gunBinCentreRemove]
                print(f'gunBC: {gunBinCentres}')
                print(f'outSigList {outerCentralSigma}')
                print(f'outFracIn: {outerFracIn}')

                plt.figure(3)
                plt.plot(gunBinC_plotting, outerCentralSigma, 'x', color=theta_colour(int(angle_list[ll_Index])), label=label_list[ll_Index])

                ll_Index += 1
            
            plt.ylabel(r'$\sigma(Δp_{T}/p_{T}^{2})$ (GeV$^{-1}$)')
            plt.xlabel(r'$p_{T}$ (GeV$^{-1}$)')
            plt.xscale('log')
            plt.yscale('log')
            plt.xlim(left=0.1)
            fontP = FontProperties() # Making legend smaller
            fontP.set_size('x-small')
            plt.legend(loc='upper right', prop=fontP)
            plt.grid(True)

            # plt.show()
            saveFile = outfile
            saveFile += f'{get}**{pow}.png'
            plt.savefig(f'{saveFile}')
            saveFilepdf = outfile
            saveFilepdf += f'{get}**{pow}.pdf'
            plt.savefig(f'{saveFilepdf}')


    return


@click.command()
@click.option('--df_CAT', '-dfCAT', "df_CAT", help='Processed csv containing the CATracks', type=str, prompt=True, multiple=True)
@click.option('--getters', '-g', help="variable(s) to plot", type=str, prompt=True, multiple=True)
@click.option('--getTruth', '-gTru', "getTruth", help="MCP truth variable(s) to plot", type=str, prompt=True, multiple=True)
# -pow MUST be in format [n,n,n]. Use one -pow [n,n,n] for each getter used.
@click.option('--powersList', '-pow', "powersList", help='Power to normalize residual to gun pT by.', type=str, prompt=True, multiple=True)
# -p0 MUST be in list of lists format [[A,mu,sigma],[A,mu,sigma]]. Use one -p0 [[A,mu,sigma]] for each getter used.
@click.option('--p0', '-p0', "p0List", help='Initial guess for bimodal parameters', type=str, prompt=True, multiple=True)
@click.option('--outfile', '-o', help="Relative filepath for output plot & filename stub", type=str, prompt=True, multiple=False)
# Example command
# python3 ../residualplotToMCPBimodalFit3Summary.py -dfCAT eff_2500_fR_pT_CATracks_disp_theta50.csv -g trkTransmom -gTru transmomMCP -pow [2] -p0 [[0.2,0,0.0003]] -o ../figures/residualToMCP_2500_p_theta50_disp_log_
# python3 ../residualplotToMCPBimodalFit3Summary.py -dfCAT eff_2500_fR_pT_CATracks_disp_theta20 -dfCAT eff_2500_fR_pT_CATracks_disp_theta30.csv -dfCAT eff_2500_fR_pT_CATracks_disp_theta40.csv -dfCAT eff_2500_fR_pT_CATracks_disp_theta50.csv -dfCAT eff_2500_fR_pT_CATracks_disp_theta60.csv -dfCAT eff_2500_fR_pT_CATracks_disp_theta70.csv -dfCAT eff_2500_fR_missing1GeV_pT_CATracks_disp_theta80.csv -dfCAT eff_2500_fR_missing0-5and1GeV_pT_CATracks_disp_theta90.csv -g trkTransmom -gTru transmomMCP -pow [2] -p0 [[0.2,0,0.0003]] -o ../figures/residualToMCP_2500_p_theta_disp_log_
def main(df_CAT, getters, getTruth, powersList, p0List, outfile):
    
    df_list, label_list, angle_list = read_files(df_CAT)

    plot_residual(df_list, label_list, angle_list, getters, getTruth, powersList, p0List, outfile)

if __name__=='__main__':
    main()