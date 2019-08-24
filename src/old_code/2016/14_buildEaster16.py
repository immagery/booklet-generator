import idml
import ePub
import appAndroid

from os import listdir
from os.path import isfile, join

import parse as p
import os
import shutil

import pprint

pp = pprint.PrettyPrinter(indent=4)

## Here is all what you need to edit
### EDIT HERE
month = "easter16"
bookletName = "Easter"
bookletSourceTexts = "Easter 2016"

monthDays = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthNames = ['January', 'February', 'March'   , 'April'  , 'May'  ,'June'    ,'July', 'August', 'September', 'October', 'November', 'December']
weekdays   = ['Monday' ,'Tuesday'  ,'Wednesday','Thursday','Friday','Saturday','Sunday']

definitions = {}

definitions["Season"] = {}
definitions["Season"]['name'] = 'Easter'
definitions["Season"]['days'] = 55
definitions["Season"]['firstDay'] = 26 # always one less
definitions["Season"]['firstMonth'] = 2 # always one less
definitions["Season"]['firstDayWeek'] = 6 # always one less
definitions["Season"]["Year"] = 2016

# write here the first page of the repeated days, starting form 0 the first day
definitions["Season"]['special_days'] = [27, 34, 37, 41, 43]
#definitions["special_days"] = [27, 33, 35, 39]

sourceBaseDirectory = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text/Easter 2016"
tempBaseDirectory = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/fileStructure/"


if os.path.exists(tempBaseDirectory):
	shutil.rmtree(tempBaseDirectory)

if not os.path.exists(tempBaseDirectory):
	os.mkdir(tempBaseDirectory)

definitions["months"]  =  []
definitions["monthLimits"] = {}

## copy of the special days for manipulation
specialDaysCount = []
for sd in definitions["Season"]['special_days']:
	specialDaysCount.append(sd)

restingDays = definitions["Season"]['days']
currentMonth = definitions["Season"]['firstMonth']
currentDay = definitions["Season"]['firstDay']
currentWeekday = definitions["Season"]['firstDayWeek']
currentDayId = 0

while restingDays > 0:
	#months definitions
	cMonth = monthNames[currentMonth]
	definitions["months"].append(cMonth)

	# define the month
	definitions["monthLimits"][cMonth] = {}
	definitions["monthLimits"][cMonth]["year"] = definitions["Season"]["Year"]
	definitions["monthLimits"][cMonth]["firstDay"] = currentDay
	definitions["monthLimits"][cMonth]["special_days"] = []

	## compute the length
	monthLength = monthDays[currentMonth] - currentDay
	if restingDays < monthLength:
		monthLength = restingDays

	## add special days
	firstCurrentDayId = currentDayId
	currentDayId = currentDayId + monthDays[currentMonth] - currentDay
	for sd in definitions["Season"]['special_days']:
		if sd < currentDayId and sd >= firstCurrentDayId:
			currentDayId = currentDayId
			if restingDays > monthLength:
				monthLength = monthLength + 1
			definitions["monthLimits"][cMonth]["special_days"].append(sd-firstCurrentDayId)

	definitions["monthLimits"][cMonth]["long"] = monthLength
	definitions["monthLimits"][cMonth]["firstWeekDay"] = currentWeekday

	currentDay = 0
	currentWeekday = (currentWeekday + monthLength) % 7
	currentMonth = (currentMonth + 1 ) % 12
	restingDays = restingDays - monthLength



onlyfiles = [f for f in listdir(sourceBaseDirectory) if isfile(join(sourceBaseDirectory, f)) and f.endswith('.txt')]

listIdx = 0
for m in definitions["months"]:
	destDir = tempBaseDirectory + '/' + m + '/'
	#print destDir
	if not os.path.exists(destDir):
		os.mkdir(destDir)
	#print definitions["monthLimits"][m]["long"]
	for i in range(definitions["monthLimits"][m]["long"]):
		shutil.copyfile(sourceBaseDirectory+"/"+onlyfiles[listIdx], destDir + onlyfiles[listIdx])
		listIdx = listIdx+1


definitions["monthFigures"] = definitions["Season"]['days']

# total number of texts
definitions["TEXTS_NUM"] = definitions["Season"]['days']
# name of the book
definitions["bookletId"] = "iPray_"+bookletName+"_"+str(definitions["Season"]["Year"])
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

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/epub/"+month+"/"
definitions["contentRoot"] 		= definitions["result"]     +"OEBPS"
definitions["contentFile"] 		= definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     		= definitions["contentRoot"]+"/toc.ncx"
definitions["finalCoverFile"]   = definitions["contentRoot"]+"/images/cover.jpeg"
definitions["finalLogoFile"]    = definitions["contentRoot"]+"/images/sub_cover.jpg"

definitions["textTemplate"] 	= definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

definitions["tableOfContentFile"] 	= definitions["contentRoot"] + "/text/tableOfContents.xhtml"
definitions["finalContentFile"] 	= definitions["contentRoot"] + "/text/content.xhtml"

### general definitions ###
definitions["bookletName"] 	= bookletName

definitions["coverFile"]    = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/cover_mid.jpg"
definitions["logoFile"]     = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/cover_in_advent.jpg"

definitions["appAndroidResult"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/AppAndroid/"

#print 'DEFINITIONS'
#pp.pprint(definitions)

print 'PROCESSING LEAFLETS!!!'

#idml
#idml.processIdmlLeaflet(definitions)

#ePub
ePub.processEpubLeaflet(definitions)

#app
#appAndroid.processAndroidLeaflet(definitions)
