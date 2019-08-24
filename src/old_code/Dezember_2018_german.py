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
definitions['firstMonth'] = 'Dezember'
definitions["firstYear"] = 2018

definitions["Season"] = {}
definitions["Season"]['name'] = 'Advent'
definitions["Season"]['firstDayWeek'] = weekdayNumber[definitions['language']]['Freitag']
definitions["Season"]['firstSeasonWeek'] = 34

definitions["Season"]['special_days'] = []

month = "12_dezember" # destination
bookletName = "Dezember 2018"
bookletSourceTexts = "Dezember 2018"

####################################################
# crear base de Datos
####################################################
baseTextsDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text/german/2018"
baseProcessDirectory = "/Volumes/Datos002/WESTPARK/iPray/german/"

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
