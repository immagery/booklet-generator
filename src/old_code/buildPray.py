#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import os
#os.environ['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

#import iPraybuild
#import iPray2019

import sys
import os
import calendar
import shutil
import json

from iPraybuild import idml, ePub, appAndroid
from iPraybuild import parse as p
from iPraybuild.database import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

sys.path.insert(0, os.path.abspath('..'))


def buildiPray( base_config,  description, design = True, epub = True, android = True, season = None ):
        
    #CREAR BASE DE DATOS
    sourceBaseDirectory = base_config["baseTextsDirectory"]+"\\"+description["bookletName"]
    DB_days = addData(sourceBaseDirectory)

    # SELECCIONAR LOS DIAS NECESARIOS
    leafletDays = selectLeafletDays(description, DB_days, season)

    print len(leafletDays), "days on the data base."

    ### general definitions ###
    description["TEXTS_NUM"] 	= len(leafletDays)
    description["bookletId"] 	= "iPray_"+description["bookletName"]+"_"+str(description["firstYear"])
    description["bookletName"] 	= description["bookletName"]
    description["globalPath"] 	= base_config["baseProcessDirectory"]+"/"+description["codeName"]+"/"
    description["codeName"]		= description["codeName"]

    basic_generator.defineSpecificVariables(description, base_config["baseProcessDirectory"])

    print 'PROCESSING LEAFLETS!!!'

    #idml
    if design:
        idml.processIdmlLeaflet(description, leafletDays)

    #ePub
    if epub:
        ePub.processEpubLeaflet(description, leafletDays)

    #app
    if android:
        appAndroid.processAndroidLeaflet(description, leafletDays)

# collect all the things to process based on a folder, it could be changed by a UI selection thing.

language = "english"
possible_languages = ["english", "german"]

if len(sys.argv) > 1:
    folder_to_proces = sys.argv[1]

if len(sys.argv) > 2:
    language_temp = sys.argv[2]
    if language_temp and language_temp not in possible_languages:
        raise Exception ( str(language_temp) + " is not a valid language.")        
    language = language_temp

config_file = open((os.path.abspath('./config.json')))
sys_config = json.loads(config_file.read())

if "info" in sys_config:
    print "Processing:", sys_config["info"]

# we could check what do we want to process, parsing different flags

# call the function to process each of them, handle exceptions so we can show them in the UI and the command line.
files_folder = []
if not os.path.isdir(os.path.abspath('.') + "\\" + sys.argv[1]):
    if not os.path.exists(os.path.abspath('.') + "\\" + sys.argv[1]):
        raise Exception ("The folder or file to process doesn't exist: "+os.path.abspath('.') + "\\" + sys.argv[1])

    input_file = os.path.abspath('.') + "\\" + sys.argv[1]
    if input_file.endswith(".json"):
        files_folder.append(os.path.abspath('.') + "\\" + sys.argv[1])
else:
    path = os.path.abspath('.') + "\\" + sys.argv[1]
    files_folder = getAllFilesRecursive(path, ".json" )

for f in files_folder:
    build_file = open((os.path.abspath('./config.json')))
    build_config = json.loads(config_file.read())
    buildiPray(json.loads()
