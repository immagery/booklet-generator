import idml
import ePub
import appAndroid

## Here is all what you need to edit
### EDIT HERE
month = "advent"
bookletName = "Advent_and_Christmas"
bookletSourceTexts = "Advent-Christmas"

definitions = {}

#months definitions
definitions["months"]  =  ['November', 'December', 'January']
definitions["monthLimits"] = {}
definitions["monthLimits"]['November'] = {}
definitions["monthLimits"]['November']["year"] = 2015
definitions["monthLimits"]['November']["firstDay"] = 29
definitions["monthLimits"]['November']["long"] = 2
definitions["monthLimits"]['November']["firstWeekDay"] = 6

definitions["monthLimits"]['December'] = {}
definitions["monthLimits"]['December']["year"] = 2015
definitions["monthLimits"]['December']["firstDay"] = 1
definitions["monthLimits"]['December']["long"] = 32
definitions["monthLimits"]['December']["firstWeekDay"] = 1

definitions["monthLimits"]['December']["special_days"] = [13]

definitions["special_days"] = ['12 - Guadalupe.txt']

definitions["monthLimits"]['January'] = {}
definitions["monthLimits"]['January']["year"] = 2016
definitions["monthLimits"]['January']["firstDay"] = 1
definitions["monthLimits"]['January']["long"] = 10
definitions["monthLimits"]['January']["firstWeekDay"] = 4


definitions["monthFigures"] = "44"

# total number of texts
definitions["TEXTS_NUM"] = 44
# name of the book
definitions["bookletId"] = "iPray_"+bookletName+"_2015"
### END EDIT

month = 'Advent'

# idml definitions
definitions["mypath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/deployment/orig/Stories/"
definitions["outPath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/deployment/dest/Stories/"

definitions["TEXT_GENERAL_DIR"] = "/Volumes/Datos002/Dropbox/3plus2/3plus2_text"
definitions["TEXT_SUBDIRS"] = [ "/"+bookletSourceTexts+"/November/",
								"/"+bookletSourceTexts+"/December/",
								"/"+bookletSourceTexts+"/January/"]

definitions["inFile"] = month+"_orig.idml"
definitions["outFile"] = month+"_dest.idml"
definitions["globalPath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/"

#ePub definitions
definitions["ePubTemplate"] = "/Volumes/Datos002/WESTPARK/iPray/epub/ePubTemplate/"

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/epub/"+month+"/"
definitions["contentRoot"] = definitions["result"]+"OEBPS"
definitions["contentFile"] = definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     = definitions["contentRoot"]+"/toc.ncx"
definitions["finalCoverFile"]     = definitions["contentRoot"]+"/images/cover.jpeg"
definitions["finalLogoFile"]     = definitions["contentRoot"]+"/images/sub_cover.jpg"

definitions["textTemplate"] = definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

definitions["tableOfContentFile"] = definitions["contentRoot"] + "/text/tableOfContents.xhtml"
definitions["finalContentFile"] = definitions["contentRoot"] + "/text/content.xhtml"

### general definitions ###
definitions["bookletName"] = bookletName

definitions["coverFile"]     = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/cover_mid.jpg"
definitions["logoFile"]     = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/cover_in_advent.jpg"

definitions["appAndroidResult"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/AppAndroid/"

#idml
idml.processIdmlLeaflet(definitions)

#ePub
ePub.processEpubLeaflet(definitions)

#app
appAndroid.processAndroidLeaflet(definitions)
