from iPraybuild import idml, ePub, appAndroid
from iPraybuild import parse as p
from . import baseTextsDirectory, baseProcessDirectory

from iPraybuild.database import *

import calendar
import os
import shutil

#from iPraybuild.gen import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

############################
# Leaflet definition
############################

definitions = {}
definitions['language'] = 'english'
definitions['days'] = 381
definitions['firstDay'] = 1
definitions['firstMonth'] = 'January'
definitions["firstYear"] = 2019

definitions["Season"] = {}
definitions["Season"]['name'] = 'Whole year'
definitions["Season"]['firstDayWeek'] = weekdayNumber[definitions['language']]['Tuesday']
definitions["Season"]['firstSeasonWeek'] = 1

definitions["Season"]['special_days'] = []

month = "2019_Complete"
bookletName = "Full year 2019"
bookletSourceTexts = "2019"

####################################################
# CREATE DATABASE
####################################################
baseTextsDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text/"
baseProcessDirectory = "/Volumes/Datos002/WESTPARK/iPray/"

sourceBaseDirectory = baseTextsDirectory+"/"+bookletSourceTexts
DB_days = addData(sourceBaseDirectory, definitions["firstYear"])


# SELECCIONAR LOS DIAS NECESARIOS
leafletDays = selectLeafletDays(definitions, DB_days, '', language = definitions['language'])

print len(leafletDays)

### general definitions ###
definitions["TEXTS_NUM"] 	= len(leafletDays)
definitions["bookletId"] 	= "iPray_"+bookletName+"_"+str(definitions["firstYear"])
definitions["bookletName"] 	= bookletName
definitions["globalPath"] 	= baseProcessDirectory+"/"+month+"/"
definitions["codeName"]		= month

basic_generator.defineSpecificVariables(definitions, baseProcessDirectory)

print 'PROCESSING LEAFLETS!!!'

#idml
#idml.processIdmlLeaflet(definitions, leafletDays)

#ePub
ePub.processEpubLeaflet(definitions, leafletDays)

#app
appAndroid.processAndroidLeaflet(definitions, leafletDays)