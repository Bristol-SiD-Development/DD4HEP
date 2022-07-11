#!/bin/sh

cd mcpFiles/
python ../gunScripts/lcio_particle_gun_500_2pT_theta85_starter.py
cd ../ddsimFiles/
ddsim --compactFile=../SiD/compact/SiD_o2_v03/SiD_o2_v03.xml --runType=batch --inputFile ../mcpFiles/mcparticles_500_2pT_theta85_starter.slcio -N=500 --outputFile=SiD_o2_v03_ddsim_500_2pT_theta85_starter.slcio
cd ../recoedFiles/
Marlin ../MarlinXMLs/muon_CAT_studies/mySiDReconstruction_o2_v03_calib1_500_2pT_theta85_starter.xml 
