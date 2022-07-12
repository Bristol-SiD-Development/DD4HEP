# DD4HEP

A repository for work on SiD for use with the DD4hep toolkit, started by Gabriel Penn as a summer student in 2016. Please feel free to direct any queries to gp13181@bristol.ac.uk.

# Getting started
These instructions assume you are SSHing to a UoB SL7 machine (e.g. sc01) with access to cvmfs. ILCSoft libraries are available on cvmfs, so you will not need to install DD4hep, LCIO, Marlin etc locally.

These instructions are based on [those provided by Dr Aidan Robson (Glasgow)](https://twiki.ppe.gla.ac.uk/bin/view/LinearCollider/GlaSiDGettingStarted), which you may find to be more up-to-date but less tailored to our setups.

## Quick start
```
mkdir iLC
cd iLC
git clone https://github.com/Bristol-SiD-Development/DD4HEP.git
cd DD4HEP
git checkout -b developPK origin/developPK
source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02/init_ilcsoft.sh
./auto/muonCATscripts/2pT_500_theta85_starter.sh
```
You can check the output with
```
anajob recoedFiles/reco_SiT_CAT_500_2pT_theta85_starter.slcio > anaj.txt
```
For the detail of what is happening in these commands go to the [Qs-breakdown](##Qs-breakdown) section.
# Directories:
 - init: initialisation scripts for environment setup
 - SiD/compact: detector descriptions (adapted from the SiD description included with lcgeo)
 - gunScripts: particle gun scripts for producing input MC particles
 - mcpFiles: source MC .slcio files to be fed into to ddsim
 - ddsimFiles: detector simulated ddsim .slcio files to be fed into to Marlin
 - MarlinXMLs: reconstruction steering files for Marlin
 - recoedFiles: store reconstructed .slcio and root files
 - analysis: pyLCIO analysis scripts, adapted from Josh Tingey's pixel studies (see pixelStudies repo)
 - auto: miscellaneous shell scripts for submitting multiple jobs or running the full chain


## iLCSoft environment
Start by setting up your environment. You will have to do this every time you start a new session, either with
```
source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02/init_ilcsoft.sh
```
... or more efficiently by adding the following to your ~/.bashrc: (remeber to restart shell session after)
```
alias ilcsoft="source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02/init_ilcsoft.sh"
```
so running `ilcsoft` will setup the environment.

# Running a simulation
There are three steps in running the full chain. 
1) Particle generation - particle gun or a physics sample
2) Detector simulation - via a ddsim command
3) Reconstruction - via a Marlin command, controlled by a xml script
## Generating input particles

For simple input events (e.g. test muons), modify a copy of an gunScripts/lcio_particle_gun_xxx.py to generate the desired particles. The particle type (PDG), momentum, phi, and theta can be changed easily. The scripts in this directory are modified from the cannonical script to give sucessive event numbers across a run with multiple momenta.

For physics events (e.g. an ILC collision), you should seek out ready-made input files, ideally in .slcio format. Older ones may use the .stdhep format, which should be compatible but may cause problems in some cases.\
Some of these can be found at:
`UPADTE when stored on sc01`

## Running detector simulation

From the ddsimFiles directory, run the following:

```
ddsim --compactFile=../SiD/compact/[GEOMETRY] --runType=batch --inputFile=[INPUT PATH] -N=[EVENTS] --outputFile=[OUTPUT PATH]
```
 - [GEOMETRY]: the path to the master .xml file for the chosen geometry
 - [INPUT PATH]: the path to the .slcio file containing the input particles. These should be contained in the mcpFiles directory
 - [EVENTS]: the desired number of events (you will of course need to have enough events in the input file!)
 - [OUTPUT PATH]: the path to the desired output file (must be .slcio)

This will simulate the events, which can then be reconstructed with Marlin.\

Putting this all together, using the quick start example gives
```
ddsim --compactFile=../SiD/compact/SiD_o2_v03/SiD_o2_v03.xml --runType=batch --inputFile ../mcpFiles/mcparticles_500_2pT_theta85_starter.slcio -N=500 --outputFile=SiD_o2_v03_ddsim_500_2pT_theta85_starter.slcio
```

## Reconstructing events

Event reconstruction is done with the Marlin package. This to controlled via a .xml steering file
You will need to have a .xml steering file for use with the Marlin reconstruction software. You can modify reco/mySiDReconstruction_o2_v03_calib1_500_2pT_theta85_starter.xml, by changing the following parameters:
 - LCIOInputFiles: path to the input file (the simulation output file)
 - DD4hepXMLFile: path to the master geometry file - this MUST be the same one that was used for the simulation
 - Under InnerPlanarDigiProcessor, ResolutionU and ResolutionV: the tracker's resolution in the u and v directions (change these e.g. to approximate pixels)
 - LCIOOutputFile: path to the desired output file.
The file name/path parameters can be eaily found by searching for "EDIT"

Navigate to your lcgeo directory (remember to initialise your environment) and run the example particle gun script:
```
python example/lcio_particle_gun.py
```
Run the simulation with the default geometry and the example input particles you have just generated:
```
ddsim --compactFile=SiD/compact/SiD_o2_v03/SiD_o2_v03.xml --runType=batch --inputFile mcparticles.slcio -N=1 --outputFile=testSiD_o2_v03.slcio
```
If this has worked, you will now have a file named testSiD_o2_v03.slcio. You can find out what data this output file contains in summary:
```
anajob testSiD_o2_v03.slcio
```
or in full detail:
```
dumpevent testSiD_o2_v3.slcio [evtNum]
```
You should now be ready to try running a reconstruction.

## Qs-breakdown
In the quick start example you have reconstructed the path of 500 2 GeV muons with the conformal tracking algorithm. \


`mkdir iLC; cd iLC; git clone ...; cd DD4HEP; git checkout -b developPK origin/developPK` \
This series of commands makes a directory to clone the Bristol DD4HEP repository into, clones it and then grabs the current working branch.\

`source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02/init_ilcsoft.sh` sets up the iLCSoft environment from the cvmfs distribution mounted to the machine. lcio, DD4hep, Marlin etc. can all now be fetched and used.

`./auto/muonCATscripts/2pT_500_theta85_starter.sh` runs a shell script that excecutes the chain in sequence from particle generation, through detector simulation to reconstruction.

**2pT_500_theta85_starter.sh**
The relative paths are set such that the script should be called from the DD4HEP repository root directory.
```
\# shebang - required for an excecutable shell script
#!/bin/sh  

\# run particle gun script and output in mcpFiles dir
cd mcpFiles/
python ../gunScripts/lcio_particle_gun_500_2pT_theta85_starter.py 
\# run detector simulation on the SiD_o2_v03 geometry and output in ddsimFiles dir
cd ../ddsimFiles/
ddsim --compactFile=../SiD/compact/SiD_o2_v03/SiD_o2_v03.xml --runType=batch --inputFile ../mcpFiles/mcparticles_500_2pT_theta85_starter.slcio -N=500 --outputFile=SiD_o2_v03_ddsim_500_2pT_theta85_starter.slcio 
\# run Marlin reconstruction and output in recoedFiles dir
cd ../recoedFiles/
Marlin ../MarlinXMLs/muon_CAT_studies/mySiDReconstruction_o2_v03_calib1_500_2pT_theta85_starter.xml 
```

## Running an example reconstruction

In order to run a reconstruction , you need a few files. The standard files can be obtained form from https://github.com/iLCSoft/SiDPerformance. You will need at least SiDReconstruction_o2_v03_calib1.xml (or similar reconstruction files) and gear_sid.xml. PandoraSettings can be ignored if you disable the MyDDMarlinPandora in the execute section of the reconstruction file (not too relevant for tracking). You will need to edit both the reconstruction and gear file so that the relevant file paths are correct for your local files. If you followed the above instructions, LCIOInputFiles is 'testSiD_o2_v03.slcio' and GearXMLFile is gear_sid.xml.  For the compact files, lcgeo/SiD/compact/SiD_o2_v03/SiD_o2_v03.xml is the current version in use (as of September 2018). You can then run the reconstruction:
```
Marlin SiDReconstruction_o2_v03_calib1.xml
```
(Don't worry about the ECal errors: this part of the reconstruction is still under development.)

You should now have a file named 'sitracks.slcio' (or whatever LCIOOutputFile was in the reconstruction file). You can run anajob or dumpevent (see above) to check its contents.

# Running the chain

Here are some general instructions for running the simulatiom->reconstruction->analysis chain. First off, you will need to set up your environment (see above). There is an old master initialisation script for this purpose, init/init_master_new.sh, but does not work for the newest version.


 
Alternatively, if you are a masochist, you can create one from scratch. Then run your reconstruction using Marlin, e.g.

```
Marlin example.xml
```

This will produce a final .slcio file containing the reconstructed tracks, which can then be analysed.

# Analysis

Analysis scripts written by Josh Tingey can be found in the analysis directory. See analysis/README.md for information and instructions. (Note: compatibility work on Josh's scripts is still a work in progress.)
