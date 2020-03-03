#!/usr/bin/env bash

# Kevin Cho
# Brigham and Women's Hospital/Harvard Medical School
# kevincho@bwh.harvard.edu

SCRIPT=$(readlink -m $(type -p $0))
SCRIPTDIR=$(dirname $SCRIPT)
dataDir=$SCRIPTDIR/data
enigmaDir=$SCRIPTDIR/data/enigmaDTI

echo Download and unzip ENIGMA data
if [ ! -d ${dataDir} ]
then
    wget http://enigma.ini.usc.edu/wp-content/uploads/2013/02/enigmaDTI.zip -P $dataDir
    unzip -o -d $enigmaDir $dataDir/enigmaDTI.zip
fi
