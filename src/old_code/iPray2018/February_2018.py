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
definitions['days'] = 29
definitions['firstDay'] = 1
definitions['firstMonth'] = 'February'
definitions["firstYear"] = 2018

definitions["Season"] = {}
definitions["Season"]['name'] = 'February'
definitions["Season"]['firstDayWeek'] = weekdayNumber['Monday']
definitions["Season"]['firstSeasonWeek'] = 10

definitions["Season"]['special_days'] = [25,]

month = "02_february"
bookletName = "February 2018"
bookletSourceTexts = "February 2018"

####################################################
# crear base de Datos
####################################################
baseTextsDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text/2018/"
baseProcessDirectory = "/Volumes/Datos002/WESTPARK/iPray/"

#CREAR BASE DE DATOS
sourceBaseDirectory = baseTextsDirectory+"/"+bookletSourceTexts
DB_days = addData(sourceBaseDirectory)

# SELECCIONAR LOS DIAS NECESARIOS
leafletDays = selectLeafletDays(definitions, DB_days, 'OT')

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
idml.processIdmlLeaflet(definitions, leafletDays)

#ePub
ePub.processEpubLeaflet(definitions, leafletDays)

#app
appAndroid.processAndroidLeaflet(definitions, leafletDays)
