import idml
import ePub
import appAndroid

from os import listdir
from os.path import isfile, join

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
definitions['days'] = 45
definitions['firstDay'] = 16
definitions['firstMonth'] = 'May'
definitions["firstYear"] = 2016

definitions["Season"] = {}
definitions["Season"]['name'] = 'OrdinaryTime'
definitions["Season"]['firstDayWeek'] = weekdayNumber['Monday']
definitions["Season"]['firstSeasonWeek'] = 7

definitions["Season"]['special_days'] = [[22, 'June', 2016]]

month = "OrdinaryTimeII"
bookletName = "OrdinaryTimeII"
bookletSourceTexts = "Ordinary time after Easter"

####################################################
# crear base de Datos
####################################################
baseTextsDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text"
baseProcessDirectory = "/Volumes/Datos002/WESTPARK/iPray/"

sourceBaseDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text/Ordinary time after Easter"
tempBaseDirectory = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/fileStructure/"

#CREAR BASE DE DATOS
season = 'ordinaryTime'
sourceBaseDirectory = baseTextsDirectory+"/Ordinary time after Easter"

DB_days = addData(sourceBaseDirectory, season)

# SELECCIONAR LOS DIAS NECESARIOS
leafletDays = selectLeafletDays(definitions)

# total number of texts
definitions["TEXTS_NUM"] = len(leafletDays)
# name of the book
definitions["bookletId"] = "iPray_"+bookletName+"_"+str(definitions["firstYear"])
### END EDIT

# idml definitions
definitions["mypath"]  = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/deployment/orig/Stories/"
definitions["outPath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/deployment/dest/Stories/"

definitions["TEXT_GENERAL_DIR"] = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text"
definitions["TEXT_SUBDIRS"] = [ "/"+bookletSourceTexts+"/" ]

definitions["inFile"] 		= month+"_orig.idml"
definitions["outFile"] 		= month+"_dest.idml"
definitions["globalPath"] 	= "/Volumes/Datos002/WESTPARK/iPray/"+month+"/"

#ePub definitions
definitions["ePubTemplate"] = "/Volumes/Datos002/WESTPARK/iPray/epub/ePubTemplate/"

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/ePub/"
definitions["contentRoot"] 		= definitions["result"]     +"OEBPS"
definitions["contentFile"] 		= definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     		= definitions["contentRoot"]+"/toc.ncx"
definitions["finalCoverFile"]   = definitions["contentRoot"]+"/images/cover.jpeg"
definitions["finalLogoFile"]    = definitions["contentRoot"]+"/images/sub_cover.jpg"

definitions["textTemplate"] 	= definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

definitions["tableOfContentFile"] 	= definitions["contentRoot"] + "/text/tableOfContents.xhtml"
definitions["finalContentFile"] 	= definitions["contentRoot"] + "/text/content.xhtml"

definitions["mobiStyleFile"] = "/Volumes/Datos002/WESTPARK/iPray/epub/mobiStyleTemplate.css"
definitions["mobiStyleFileDestination"] = "/OEBPS/Styles/Stylesheet.css"

### general definitions ###
definitions["bookletName"] 	= bookletName

definitions["coverFile"]    = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/cover_mid.jpg"
definitions["logoFile"]     = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/cover_in_advent.jpg"

definitions["appAndroidResult"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/AppAndroid/"

#print 'DEFINITIONS'
#pp.pprint(definitions)

print 'PROCESSING LEAFLETS!!!'

#idml
idml.processIdmlLeaflet(definitions)

#ePub
ePub.processEpubLeaflet(definitions, leafletDays)

#app
appAndroid.processAndroidLeaflet(definitions, leafletDays)
