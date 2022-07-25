#--------------------------------------------------------------
# Track collection to be used as clic option?
#
# Test other method of dict keys
#
# Make sure works in case of multiple true tracks...
# ... i.e. get multiple true tracks in same evt (from diff mcp)
# ... cross check with doubleTrue.py
#
# add 3rd element to trkTup? i.e. (trk, pur, best?)-> dont think so
# or assign best track to variable? -> this 
# Keep current with the mcp associated as 3rd element -> useful later...?
#
# When to write hitInfo to dict 
# now rearrange to make list of trkTuples
#--------------------------------------------------------------
from __future__ import division
from collections import Counter, OrderedDict, defaultdict
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

def extract_track_properties(track):                                            
	"""Extract properties & track parameters from track.          
	
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
	trackOmega : float
		omega of the track
	trackD0 : float
		d0 of the track
	trackZ0 : float
		z0 of the track
	trackRefP : list
		3 vec position of track reference point
	"""
	c = 2.99792*10**11                                                          
	#Transverse momentum related to omega, momentum related to tan(lambda)
	tracktransmom = math.fabs(c*10**(-15)*5/track.getOmega())                  
	trackmom = tracktransmom*(1+track.getTanLambda()**2)**0.5
	trackphi = track.getPhi()
	#theta also related to tan(lambda)
	tracktheta = math.pi/2.-math.atan(track.getTanLambda())   
	trackOmega = track.getOmega()     
	trackD0 = track.getD0()  
	trackZ0 = track.getZ0()
	trackRefP = []
	refP = track.getReferencePoint()
	for i in range(3): # ref P is contained in the first 3 elements
		trackRefP.append(refP[i])

	return (trackmom, tracktransmom, trackphi, tracktheta, trackOmega, trackD0, trackZ0, trackRefP)

def add_to_dict(datadict, evtNum, trkPTup, good, nSharedHits, nMissingHits, nExtraHits, hitInfo):
	"""Add properties & track parameters to the datadict for later writing.     
	
	Arguments
	---------
	datadict : dict
		Dictionary to write the data out to
	evtNum : int
		Event number to associate the data to
	trkPTup : tuple - (ROOT.IOIMPL.TrackIOImpl, float, ROOT.IOIMPL::MCParticleIOImpl)
		Tuple containing the track to be added & its purity
	good : Bool
		Indicates if track is the chosen 'True' track or is a fake (False).
		
	
	Returns
	------
	Procedural - acts on dict provided
	"""
	mom, trMom, phi, theta, omega, d0, z0, refP = extract_track_properties(trkPTup[0])
	datadict['evtNum'].append(evtNum)
	datadict['goodTrk'].append(good)
	datadict['trkMom'].append(mom)
	datadict['trkTransmom'].append(trMom)
	datadict['trkPhi'].append(phi)
	datadict['trkTheta'].append(theta)
	datadict['trkOmega'].append(omega)
	datadict['trkD0'].append(d0)
	datadict['trkZ0'].append(z0)
	datadict['trkPurity'].append(trkPTup[1])
	datadict['trkRefP'].append(refP)
	datadict['nSharedHits'].append(nSharedHits)
	datadict['nMissingHits'].append(nMissingHits)
	datadict['nExtraHits'].append(nExtraHits)
	datadict['hitInfo'].append(hitInfo)

	return

def trkHit_to_mcp(hitDict, trkHit):
	"""Get the monte carlo particle that caused the track hit.
		Required as usual dict methods do not work with these objects      
	
	Arguments
	---------
	hitDict : dict
		Dictionary mapping all the trkHits to the MCP, i.e. {ROOT.IOIMPL::TrackerHitPlaneIOImpl : ROOT.IOIMPL::MCParticleIOImpl}
	trkHit : ROOT.IOIMPL::TrackerHitPlaneIOImpl
		Tracker hit to find the associated MCP for.

	Returns
	------
	mcp : ROOT.IOIMPL::MCParticleIOImpl
		The MCP that caused the hit
	"""
	
	trkHitsObjs = hitDict.keys()
	for trkHO in trkHitsObjs:
		if trkHO == trkHit:
			mcp = hitDict[trkHO]
		
	return mcp

def count_mcp(mcpObjList):
	"""Find the number of unique MCPs that are contained in the list of MCP objects.
		Find the PDG ID of these MCPs.
	
	Arguments
	---------
	mcpObjList : [ROOT.IOIMPL::MCParticleIOImpl]
		List of MCP objects 

	Returns
	------
	len(mcpDict) : int
		The number of unique MCPs in the 
	mcpDict : dict
		'Counter style' dictionary {ROOT.IOIMPL::MCParticleIOImpl : nOccurances}
	pdgList : [int]
		List of the PDG IDs of the corresponding MCPs in the mcpDict
	"""
	mcpDict = defaultdict(int)
	for mcpObj in mcpObjList:
		keys = mcpDict.keys()
		key = mcpObj
		for k in keys:
			if k == mcpObj:
				key = k
		mcpDict[key] += 1
	
	pdgList = []
	for mcp in mcpDict:
		pdg = mcp.getPDG()
		pdgList.append(pdg)

	return(len(mcpDict), mcpDict, pdgList)

def comp_tuple_maker(mcpObjList):
	"""Produce summary tuples of a list of mcpObjects.
	
	Arguments
	---------
	mcpObjList : [ROOT.IOIMPL::MCParticleIOImpl]
		List of MCP objects 

	Returns
	------
	outTups : [(ROOT.IOIMPL::MCParticleIOImpl, int, int)
		[(mcpObject, occurnaces in the list, PDG ID)]
	"""
	outTups = []
	nUnique, mcpDict, pdgList = count_mcp(mcpObjList)
	for i in range(nUnique):
		tup = (mcpDict.keys()[i], mcpDict.values()[i], pdgList[i])
		outTups.append(tup)

	return outTups

def compare_tracks(targetTrk, compTrk, hitDict):
	"""Find the similarites and differneces between the hits of two tracks
		Often used to compare a good track (targetTrk) to a fake (compTrk)
	Arguments
	---------
	targetTrk : ROOT.IOIMPL.TrackIOImpl
		The track to which the hits are comapred
	compTrk : ROOT.IOIMPL.TrackIOImpl
		The track being compared to the targetTrk
	hitDict : dict
		Dictionary mapping all the trkHits to the MCP, i.e. {ROOT.IOIMPL::TrackerHitPlaneIOImpl : ROOT.IOIMPL::MCParticleIOImpl}
	

	Returns
	------
	extraHits : [ROOT.IOIMPL::TrackerHitPlaneIOImpl]
		List of the hits in the compTrk that are NOT in the targetTrk
	extraTuples : [(ROOT.IOIMPL::MCParticleIOImpl, int, int)]
		List of tuples containing the MCP, number of hits caused by this MCP and the PDG ID of the MCP
		i.e. (mcp, n, PDG)
	missingHits : [ROOT.IOIMPL::TrackerHitPlaneIOImpl]
		List of the hits in the targetTrk that are NOT in the compTrk
	missingTuples : [(ROOT.IOIMPL::MCParticleIOImpl, int, int)]
		List of tuples containing the MCP, number of hits caused by this MCP and the PDG ID of the MCP
		i.e. [(mcp, n, PDG)]
	sharedHits : [ROOT.IOIMPL::TrackerHitPlaneIOImpl]
		List of the hits in BOTH the compTrk and the targetTrk
	sharedTuples : [(ROOT.IOIMPL::MCParticleIOImpl, int, int)]
		List of tuples containing the MCP, number of hits caused by this MCP and the PDG ID of the MCP
		i.e. (mcp, n, PDG)
	"""
	targetHits = targetTrk.getTrackerHits()
	compHits = compTrk.getTrackerHits()

	extraHits = []
	extraHitsMCP = []
	missingHits = []
	missingHitsMCP = []
	sharedHits = []
	sharedHitsMCP = []

	for cHit in compHits:
		mcp = trkHit_to_mcp(hitDict, cHit)

		if cHit not in targetHits:
			extraHits.append(cHit)
			extraHitsMCP.append(mcp)
		if cHit in targetHits:
			sharedHits.append(cHit)
			sharedHitsMCP.append(mcp)
	
	for tHit in targetHits:
		mcp = trkHit_to_mcp(hitDict, tHit)
		if tHit not in compHits:
			missingHits.append(tHit)
			missingHitsMCP.append(mcp)
	
	extraTuples = comp_tuple_maker(extraHitsMCP)
	missingTuples = comp_tuple_maker(missingHitsMCP)
	sharedTuples = comp_tuple_maker(sharedHitsMCP)

	return (extraHits, extraTuples, missingHits, missingTuples, sharedHits, sharedTuples)

def extract_hit_info(track, hitDict):

	hitInfo = []
	for trkHit in track.getTrackerHits():
		mcp = trkHit_to_mcp(hitDict, trkHit)
		pdgID = count_mcp([mcp])[2][0]
		x, y, z = (trkHit.getPosition()[0], trkHit.getPosition()[1], trkHit.getPosition()[2])
		hitInfo.append([pdgID, (x, y, z)])
	
	return hitInfo

def get_data(infile, outfile):
	print("infile: {}, outfile: {}\n".format(infile, outfile))

	# Create required empty lists in datadict for each getter method
	datadict = OrderedDict()
	datadict['evtNum'] = []
	datadict['goodTrk'] = []
	datadict['trkMom'] = []
	datadict['trkTransmom'] = []
	datadict['trkPhi'] = []
	datadict['trkTheta'] = []
	datadict['trkOmega'] = []
	datadict['trkD0'] = []
	datadict['trkZ0'] = []
	datadict['trkPurity'] = []
	datadict['trkRefP'] = []
	datadict['nSharedHits'] = []
	datadict['nMissingHits'] = []
	datadict['nExtraHits'] = []
	datadict['hitInfo'] = []
	# datadict['nHits'] = []
	# nTrksFoundList = []

	evtNum = 0

	for inFi in infile:

		# pyLCIO routine to use getter methods to read from `.slcio`
		reader = IOIMPL.LCFactory.getInstance().createLCReader()
		reader.open(str(inFi))

		for event in reader:

			fakeCounter = 0

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
			
			### EDIT - Input track collection name to be used
			# tracks = event.getCollection('CATracks')
			tracks = event.getCollection('SiTracks')
			######################################################

			# dict to hold candidate good tracks in format
			# {MCP : [(trkPurityTuple1), (trkPurityTuple2), ...]}
			pureTrksDict = defaultdict(list)
			# Holds final fake tracks
			fakeTrksList = []
			# Hold the MCP assoc. w/ the trker hit in format
			# {trkHit: mcp}
			hitDict = {}
			
			# print('###', len(tracks), 'tracks made in event')
			for track in tracks:
				# flag to indicate if track is real or fake 
				pureTrk = False
				hitsOnTrack = []
				hitMCP = []
				for tHit in track.getTrackerHits():
					hitsOnTrack.append(tHit)
				#### Very slow way to do this!!! 
				# Want trkHit -> simHit -> mcp
				# Need to get trk Hit -> simHit some how #### 
				for trkHit in hitsOnTrack:
					for simHitCol, hitRel in zip((vtxBarHits, vtxEndHits, trkBarHits, trkEndHits), (vtxBarHitsRels, vtxEndHitsRels, trkBarHitsRels, trkEndHitsRels)):
						for simHit, hRel in zip(simHitCol, hitRel):
							if hRel.getFrom() == trkHit:
								# Chain together getter methods?
								mcp = simHit.getMCParticle()
								hitMCP.append(mcp)
								hitDict[trkHit] = mcp

				maxPurity = -1
				for mcp in MCParticles:
					hCount = hitMCP.count(mcp)
					purity = hCount/len(hitsOnTrack)
					# trkPurTuple = (track, purity, mcp)
					if purity > 0.8:
						trkPurTuple = (track, purity, mcp)
						pureTrk = True
						keys = pureTrksDict.keys()
						key = mcp
						for k in keys:
							if k == mcp:
								key = k
						pureTrksDict[key].append(trkPurTuple)
					elif purity > maxPurity:
						trkPurTuple = (track, purity, mcp)
						maxPurity = purity

						'''# or could be?
						key = mcp
						for k in pureTrksDict:
							if k == mcp:
								key = k
						pureTrksDict[key].append(track)'''
						

				if not pureTrk:
					fakeTrksList.append(trkPurTuple)
					fakeCounter += 1
			# end loop over tracks

			# Look at all the tracks in the evt 
			goodTrackTuples = []
			for trkMCP in pureTrksDict:
				if len(pureTrksDict[trkMCP]) > 1: # Need to pick out the 'True' track for this mcp
					trksMom = []
					trksPurity = []
					for trkTup in pureTrksDict[trkMCP]:
						trksMom.append(extract_track_properties(trkTup[0])[0])
						trksPurity.append(trkTup[1])
					# Choose trk with greatest purity (momentum tie break) as the good track
					maxPurity = max(trksPurity)
					# gets index (indicies) of trk w/ with greatest purity
					maxIndex = [i for i, x in enumerate(trksPurity) if x == maxPurity]
					if len(maxIndex) > 1: # use highest momentum as tie breaker
						maxMom = max(trksMom[mI] for mI in maxIndex)
						maxIndex = trksMom.index(maxMom) # could cause issue if identical values (v. unlikely?)
					else: # remembering in a list
						maxIndex = maxIndex[0]
					goodTrackTuples.append(pureTrksDict[trkMCP][maxIndex])
					# All other tracks associated with this mcp are thus fake tracks
					# Remove best track
					del pureTrksDict[trkMCP][maxIndex]
					for trkTup in pureTrksDict[trkMCP]:
						fakeTrksList.append(trkTup)
						fakeCounter += 1
				else: # only 1 track so this is the good track
					goodTrackTuples.append(pureTrksDict[trkMCP][0])
				
			if len(goodTrackTuples) > 1:
				print('\n### Multiple good tracks found in event {}\n'.format(evtNum))
			elif len(goodTrackTuples) == 0:
				print('\n### No good tracks found in event {}\n'.format(evtNum))
				
			for goodTrkT in goodTrackTuples:
				goodTrk = goodTrkT[0]
				trkMom = extract_track_properties(goodTrk)[0]
				hitInfo = extract_hit_info(goodTrk, hitDict)
				add_to_dict(datadict, evtNum, goodTrkT, True, float('NaN'), float('NaN'), float('NaN'), hitInfo)


			for fakeTrkT in fakeTrksList:
				fakeTrk = fakeTrkT[0]
				trkMom = extract_track_properties(fakeTrk)[0]
				hitInfo = extract_hit_info(fakeTrk, hitDict)

				extraHits, extraTuples, missingHits, missingTuples, sharedHits, sharedTuples = compare_tracks(goodTrk, fakeTrk, hitDict)
				add_to_dict(datadict, evtNum, fakeTrkT, False, len(sharedHits), len(missingHits), len(extraHits), hitInfo)
				# Could add tuples to output dict
				print('extraTupL: ', extraTuples)
				print('missTupL: ', missingTuples)
				print('sharedTupL: ', sharedTuples)

			if fakeCounter > 1:
				print(fakeCounter, 'fake tracks found in evt', evtNum)
			
			evtNum += 1
			if evtNum % 1000 == 0:
				print(evtNum, 'events processed')
		# end loop over events

	# check no. entries in each column
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
	 