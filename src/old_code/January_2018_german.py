from iPraybuild import idml, ePub, appAndroid
from iPraybuild import parse as p

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
definitions['language'] = 'german'
definitions['days'] = 31
definitions['firstDay'] = 1
definitions['firstMonth'] = 'Januar'
definitions["firstYear"] = 2019

definitions["Season"] = {}
definitions["Season"]['name'] = 'Advent'
definitions["Season"]['firstDayWeek'] = weekdayNumber[definitions['language']]['Dienstag']
definitions["Season"]['firstSeasonWeek'] = 32

definitions["Season"]['special_days'] = []

month = "1_januar" # destination
bookletName = "Januar 2019"
bookletSourceTexts = "Januar 2019"

####################################################
# crear base de Datos
####################################################
baseTextsDirectory = "C:\\Users\\me\\Dropbox\\3plus2\\3plus2_text\\german\\2019"
baseProcessDirectory = "F:\\iPray\\german"

print "\n\n>>>>>>>        {0}(German version)        <<<<<<<".format(bookletName.upper())

#CREAR BASE DE DATOS
sourceBaseDirectory = baseTextsDirectory+"/"+bookletSourceTexts
DB_days = addData(sourceBaseDirectory, definitions["firstYear"])

# SELECCIONAR LOS DIAS NECESARIOS
leafletDays = selectLeafletDays(definitions, DB_days, 'OT', language = definitions['language'])

print "Days ready for the leaflet", len(leafletDays)

### general definitions ###
definitions["TEXTS_NUM"] 	= len(leafletDays)
definitions["bookletId"] 	= "iPray_"+bookletName+"_"+str(definitions["firstYear"])
definitions["bookletName"] 	= bookletName
definitions["globalPath"] 	= baseProcessDirectory+"/"+month+"/"
definitions["codeName"]		= month

basic_generator.defineSpecificVariables(definitions, baseProcessDirectory)

print "\nGENERATE LEAFLETS!!!"

#idml
idml.processIdmlLeaflet(definitions, leafletDays)

#ePub
ePub.processEpubLeaflet(definitions, leafletDays)

#app
appAndroid.processAndroidLeaflet(definitions, leafletDays)
