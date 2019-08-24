import idml
import ePub
import appAndroid

import parse as p
import os
import shutil

import basic_generator
from gen import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

import calendar

############################
# Leaflet definition
############################

definitions = {}
definitions['days'] = 32
definitions['firstDay'] = 1
definitions['firstMonth'] = 'July'
definitions["firstYear"] = 2017

definitions["Season"] = {}
definitions["Season"]['name'] = 'OT'
definitions["Season"]['firstDayWeek'] = weekdayNumber['Saturday']
definitions["Season"]['firstSeasonWeek'] = 12

definitions["Season"]['special_days'] = [11]

month = "07_july"
bookletName = "July 2017"
bookletSourceTexts = "July 2017"

####################################################
# crear base de Datos
####################################################
baseTextsDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text/2017"
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
