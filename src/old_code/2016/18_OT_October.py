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
definitions['days'] = 33
definitions['firstDay'] = 1
definitions['firstMonth'] = 'October'
definitions["firstYear"] = 2016

definitions["Season"] = {}
definitions["Season"]['name'] = 'OrdinaryTime'
definitions["Season"]['firstDayWeek'] = weekdayNumber['Saturday']
definitions["Season"]['firstSeasonWeek'] = 26

definitions["Season"]['special_days'] = [[7, 'October', 2016], [13, 'October', 2016]]

month = "October2016"
bookletName = "October2016"
bookletSourceTexts = "October 2016"

####################################################
# crear base de Datos
####################################################
baseTextsDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text"
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
