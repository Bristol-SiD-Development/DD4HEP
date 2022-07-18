#--------------------------------------------------------------
# TODO command line input for best track selection criteria
# TODO sequential evt numbers - Done - check this
# TODO commadn line input to select track clollection used
#--------------------------------------------------------------
from __future__ import division
from collections import Counter, OrderedDict
import ROOT
import csv #not using pandas due to numpy issues
import click
import sys
import math

from pyLCIO import IOIMPL
from pyLCIO import UTIL
from pyLCIO import EVENT
from pyLCIO import IOIMPL

from ROOT import *

def extract_mcparticle_properties(mcparticle):
	"""Extracts properties (momentum, transmom, phi, theta & PDG id)  from mcparticle.
	
	Arguments
	--------
	mcparticle : ROOT.IOIMPL.MCParticleIOImpl
		MCParticle to extract properties from
	Returns
	-------
	mcparticlemom : float
		Momentum of mcparticle
	mcparticletransmom : float
		transverse momentum  of mcparticle
	mcparticlephi : float
		phi of mcparticle
	mcparticletheta : float
		theta of mcparticle
	mcparticlePDG : int
		PDG id
	"""
	#Only first 3 elements of mcparticle.getMomentum() contain information;
	#can't get more than one element at once
	mcparticlemomx, mcparticlemomy, mcparticlemomz = (
			mcparticle.getMomentum()[0], mcparticle.getMomentum()[1], mcparticle.getMomentum()[2])
	mcparticlemom = (mcparticlemomx**2+mcparticlemomy**2+mcparticlemomz**2)**0.5                                              
	mcparticletransmom = (mcparticlemomx**2+mcparticlemomy**2)**0.5     
	mcparticlephi = math.atan2(mcparticlemomy, mcparticlemomx)
	mcparticletheta = math.atan2(mcparticletransmom,mcparticlemomz)
	mcparticlePDG = mcparticle.getPDG()

	return (mcparticlemom, mcparticletransmom, mcparticlephi, mcparticletheta, mcparticlePDG)

def extract_track_properties(track):                                            
	"""Extract properties (momentum, transverse momentum phi and theta) from track.          
	
	Arguments
	---------
	track : ROOT.IOIMPL.TrackIOImpl
		Track to extract properties from
	
	Returns
	------
	trackmom : float
		Momentum of track
	tracktransmom : float
		Transverse momentum of track
	trackphi : float
		phi of track
	tracktheta : float
		theta of track
	"""
	c = 2.99792*10**11                                                          
																		  
	#Transverse momentum related to omega, momentum related to tan(lambda)
	tracktransmom = math.fabs(c*10**(-15)*5/track.getOmega())                  
	trackmom = tracktransmom*(1+track.getTanLambda()**2)**0.5
	trackphi = track.getPhi()
	#theta also related to tan(lambda)
	tracktheta = math.pi/2.-math.atan(track.getTanLambda())                     
	return (trackmom, tracktransmom, trackphi, tracktheta)

def get_data(infile, outfile):
	print("infile: {}, outfile: {}\n".format(infile, outfile))

	# Create required empty lists in datadict for each getter method
	datadict = OrderedDict()
	datadict['evtNum'] = []
	datadict['pdgMCP'] = []
	datadict['momMCP'] = []
	datadict['transmomMCP'] =[]
	datadict['phiMCP'] = []
	datadict['thetaMCP'] = []
	datadict['trkMom'] = []
	datadict['trkTransmom'] = []
	datadict['trkPhi'] = []
	datadict['trkTheta'] = []
	datadict['nGoodHits'] = []
	datadict['nHits'] = []
	datadict['trkPurity'] = []
	nTrksFoundList = []

	evtNum = 0

	for inFi in infile:

		# pyLCIO routine to use getter methods to read from `.slcio`
		reader = IOIMPL.LCFactory.getInstance().createLCReader()
		# reader.open(str(infile[i]))
		reader.open(str(inFi))

		for event in reader:
			MCParticles = event.getCollection('MCParticle')
			# SiVertexBarrelHitsRelations SiVertexEndcapHitsRelations SiTrackerBarrelHitsRelations SiTrackerEndcapHitsRelations
			vtxBarHits = event.getCollection('SiVertexBarrelHits')
			vtxBarHitsRels = event.getCollection('SiVertexBarrelHitsRelations')
			vtxEndHits = event.getCollection('SiVertexEndcapHits')
			vtxEndHitsRels = event.getCollection('SiVertexEndcapHitsRelations')
			trkBarHits = event.getCollection('SiTrackerBarrelHits')
			trkBarHitsRels = event.getCollection('SiTrackerBarrelHitsRelations')
			trkEndHits = event.getCollection('SiTrackerEndcapHits')
			trkEndHitsRels = event.getCollection('SiTrackerEndcapHitsRelations')
			# evtNum = event.getEventNumber()
			# print(evtNum)
			for mcp in MCParticles:
				# flag to indicate if track is found for this MCP
				trackFound = False
				nTrksFound = 0
				goodTrks = []
				goodTrksMom = []
				goodTrksTransmom = []
				goodTrksPhi = []
				goodTrksTheta = []
				goodTrksnGoodHits = []
				goodTrksnHits = []
				goodTrksPurity = []
				datadict['evtNum'].append(evtNum)
				datadict['momMCP'].append(extract_mcparticle_properties(mcp)[0])
				datadict['transmomMCP'].append(extract_mcparticle_properties(mcp)[1])
				datadict['phiMCP'].append(extract_mcparticle_properties(mcp)[2])
				datadict['thetaMCP'].append(extract_mcparticle_properties(mcp)[3])
				datadict['pdgMCP'].append(extract_mcparticle_properties(mcp)[4])
				trkHitsAssociatedWithThisMCParticle = []
				for simHitCol, hitRel in zip((vtxBarHits, vtxEndHits, trkBarHits, trkEndHits), (vtxBarHitsRels, vtxEndHitsRels, trkBarHitsRels, trkEndHitsRels)):
					print("simHitCol: ", simHitCol.getNumberOfElements, "hitRel: ", hitRel.getNumberOfElements)
					for simHits, hRel in zip(simHitCol, hitRel):
						if simHits.getMCParticle() == mcp:
							# print("Matched simHit to this MCParticle")
							print("hitRel gives: ", hRel.getFrom())
							trkHitsAssociatedWithThisMCParticle.append(hRel.getFrom())
					# end loop over the simHits & hitRelations
				# end loop over simHits & hitsRealtions COLLECTIONS
				# print(len(trkHitsAssociatedWithThisMCParticle), 'trkHitsAssociatedWithThisMCParticle: ', trkHitsAssociatedWithThisMCParticle)
				# Now have list with all the tracker hits associated with the given MCParticle 
				tracks = event.getCollection('CATracks')
				for track in tracks:
					hitsOnTrack = []
					trackHits = track.getTrackerHits()
					for i in trackHits:
						hitsOnTrack.append(i)
					# print(len(hitsOnTrack),'hitsOnTrack: ', hitsOnTrack)
					# goodHits = set(trkHitsAssociatedWithThisMCParticle).intersection(set(hitsOnTrack))
					goodHits = [x for x in hitsOnTrack if x in trkHitsAssociatedWithThisMCParticle]
					purity = (len(goodHits))/(len(hitsOnTrack))
					# print(len(goodHits),'goodHits: ', goodHits)
					if purity > 0.8: # TODO add cmd line option to set this value or other param
									# e.g. n goodHits > value
						trackFound = True
						nTrksFound += 1
						goodTrks.append(track)
						goodTrksnGoodHits.append(len(goodHits))
						goodTrksnHits.append(len(hitsOnTrack))
						goodTrksPurity.append(purity)
						goodTrksMom.append(extract_track_properties(track)[0])
						goodTrksTransmom.append(extract_track_properties(track)[1])
						goodTrksPhi.append(extract_track_properties(track)[2])
						goodTrksTheta.append(extract_track_properties(track)[3])
				# end loop over tracks 
				# Select good trk with highest momentum
				if trackFound:
					maxMom = max(goodTrksMom)
					maxIndex = goodTrksMom.index(maxMom) # could cause issue if identical values (v. unlikely?)
					# print('goodTrksMom:', goodTrksMom, '\nmaxMom:', maxMom, 'maxIndex:', maxIndex)
					datadict['nGoodHits'].append(goodTrksnGoodHits[maxIndex])
					datadict['nHits'].append(goodTrksnHits[maxIndex])
					datadict['trkPurity'].append(goodTrksPurity[maxIndex])
					datadict['trkMom'].append(goodTrksMom[maxIndex])
					datadict['trkTransmom'].append(goodTrksTransmom[maxIndex])
					datadict['trkPhi'].append(goodTrksPhi[maxIndex])
					datadict['trkTheta'].append(goodTrksTheta[maxIndex])
				# if no track associated fill with nan
				if not trackFound:
					datadict['nGoodHits'].append(float('NaN'))
					datadict['nHits'].append(float('NaN'))
					datadict['trkPurity'].append(float('NaN'))
					datadict['trkMom'].append(float('NaN'))
					datadict['trkTransmom'].append(float('NaN'))
					datadict['trkPhi'].append(float('NaN'))
					datadict['trkTheta'].append(float('NaN'))
				
				nTrksFoundList.append(nTrksFound)
			# end loop over MCParticles
			# finished processing event so increment evtNum
			evtNum += 1
		# end loop over events
	# print('\n datadict', datadict)
	print(Counter(nTrksFoundList))
	
	for x in datadict:
		print(len(datadict[x]))
		
	zipdatadict = zip(*datadict.values()) # zipped dict to write corresponding data in rows, same data in columns
	with open(outfile,'wb') as f: # need 'wb' method in py2
		writer = csv.writer(f)
		writer.writerow(datadict.keys()) # write header row
		writer.writerows(zipdatadict)

	reader.close()
	return

@click.command()
@click.option('--infile', '-i', help="Input slcio file", type=str, prompt=True, multiple=True)
@click.option('--outfile', '-o', help="Output csv file", type=str, prompt=True)

def main(infile, outfile):

	get_data(infile, outfile)

if __name__=='__main__':
 	main()
	 