# DD4HEP

A repository for work on SiD for use with the DD4hep toolkit, started by Gabriel Penn as a summer student in 2016. Please feel free to direct any queries to gp13181@bristol.ac.uk.

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

# Getting started
These instructions assume you are SSHing to a UoB SL7 machine (e.g. sc01) with access to cvmfs. ILCSoft libraries are available on cvmfs, so you will not need to install DD4hep, LCIO, Marlin etc locally.

These instructions are based on [those provided by Dr Aidan Robson (Glasgow)](https://twiki.ppe.gla.ac.uk/bin/view/LinearCollider/GlaSiDGettingStarted), which you may find to be more up-to-date but less tailored to our setups.

## Installing lcgeo
Start by setting up your environment. You will have to do this every time you start a new session:
```
<!-- source /cvmfs/sft.cern.ch/lcg/releases/gcc/4.9.3/x86_64-slc6/setup.sh -->

source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02/init_ilcsoft.sh
```
Or add the following to your ~/.bashrc: (remeber to restart shell session after)
```
alias ilcsoft="source /cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02/init_ilcsoft.sh"
```
so running `ilcsoft` will setup the environment.

Navigate to the directory in which you wish to install lcgeo and checkout the source code:
```
git clone https://github.com/iLCSoft/lcgeo.git
```
Remove some unfinished calorimeter files:
```
rm lcgeo/detector/calorimeter/SHcal*
rm lcgeo/detector/calorimeter/SEcal*
rm lcgeo/detector/CaloTB/CaloPrototype*
```
Create and move to the build directory:
```
mkdir lcgeo/build
cd lcgeo/build
```
Make the installation:
```
cmake -DCMAKE_CXX_COMPILER=$(which g++) -DCMAKE_C_COMPILER=$(which gcc) -C /cvmfs/ilc.desy.de/sw/x86_64_gcc49_sl6/v02-00-01/ILCSoft.cmake ..
cmake -DCMAKE_CXX_COMPILER=$(which g++) -DCMAKE_C_COMPILER=$(which gcc) -DILCUTIL_DIR=/cvmfs/ilc.desy.de/sw/x86_64_gcc49_sl6/v02-00-01/ILCSoft.cmake -C $ILCSOFT/ILCSoft.cmake ..
make -j4
make install
```
If this runs without throwing any errors, you should now be able to run the example simulation.
Note: The Glasgow instructions suggests running:
```
source ../bin.thislcgeo.sh
```
but running it will cause ddsim to not work (something to do with PYTHONPATH priorites).

## Running an example sim
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
dumpevent testSiD_o2_v3.slcio 1
```
You should now be ready to try running a reconstruction.

## Running an example reconstruction

In order to run a reconstruction , you need a few files. The standard files can be obtained form from https://github.com/iLCSoft/SiDPerformance. You will need at least SiDReconstruction_o2_v03_calib1.xml (or similar reconstruction files) and gear_sid.xml. PandoraSettings can be ignored if you disable the MyDDMarlinPandora in the execute section of the reconstruction file (not too relevant for tracking). You will need to edit both the reconstruction and gear file so that the relevant file paths are correct for your local files. If you followed the above instructions, LCIOInputFiles is 'testSiD_o2_v03.slcio' and GearXMLFile is gear_sid.xml.  For the compact files, lcgeo/SiD/compact/SiD_o2_v03/SiD_o2_v03.xml is the current version in use (as of September 2018). You can then run the reconstruction:
```
Marlin SiDReconstruction_o2_v03_calib1.xml
```
(Don't worry about the ECal errors: this part of the reconstruction is still under development.)

You should now have a file named 'sitracks.slcio' (or whatever LCIOOutputFile was in the reconstruction file). You can run anajob or dumpevent (see above) to check its contents.

# Running the chain

Here are some general instructions for running the simulatiom->reconstruction->analysis chain. First off, you will need to set up your environment (see above). There is an old master initialisation script for this purpose, init/init_master_new.sh, but does not work for the newest version.

## Generating input particles

For simple input events (e.g. test muons), modify a copy of lcio_particle_gun.py to generate the desired particles. The particle type (PDG), momentum, phi, and theta can be changed easily.

For more complicated events (e.g. an ILC collision), you may need to seek out ready-made input files. Older ones may use the .stdhep format, which should be compatible but may cause problems in some cases.

## Running a simulation

From the lcgeo directory, run the following:

```
ddsim --compactFile=compact/[GEOMETRY] --runType=batch --inputFile=[INPUT PATH] -N=[EVENTS] --outputFile=[OUTPUT PATH]
```
 - [GEOMETRY]: the path to the master .xml file for the chosen geometry
 - [INPUT PATH]: the path to the .slcio file containing the input particles
 - [EVENTS]: the desired number of events (you will of course need to have enough events in the input file!)
 - [OUTPUT PATH]: the path to the desired output file (must be .slcio)

This will simulate the events, which can then be reconstructed.

## Reconstructing events

You will need to have a .xml steering file for use with the Marlin reconstruction software. You can modify reco/SiDReconstruction_test160628.xml, SiDReconstruction_o2_v03_calib1.xml, by changing the following parameters:
 - LCIOInputFiles: path to the input file (the simulation output file)
 - DD4hepXMLFile: path to the master geometry file - this MUST be the same one that was used for the simulation
 - Under InnerPlanarDigiProcessor, ResolutionU and ResolutionV: the tracker's resolution in the u and v directions (change these e.g. to approximate pixels)
 - LCIOOutputFile: path to the desired output file.
 
Alternatively, if you are a masochist, you can create one from scratch. Then run your reconstruction using Marlin, e.g.

```
Marlin example.xml
```

This will produce a final .slcio file containing the reconstructed tracks, which can then be analysed.

# Analysis

Analysis scripts written by Josh Tingey can be found in the analysis directory. See analysis/README.md for information and instructions. (Note: compatibility work on Josh's scripts is still a work in progress.)
