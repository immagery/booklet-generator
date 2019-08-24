import idml
import ePub
import appAndroid

month = "october"
bookletName = "October"
bookletSourceTexts = "11_November"

# idml definitions
definitions = {}
definitions["mypath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/deployment/orig/Stories/"
definitions["outPath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/deployment/dest/Stories/"

definitions["TEXTS_NUM"] = 31
definitions["TEXT_GENERAL_DIR"] = "/Users/chus/Dropbox/3plus2/3plus2_text"
definitions["TEXT_SUBDIRS"] = ["/10_October/"]

definitions["inFile"] = month+"_orig.idml"
definitions["outFile"] = month+"_dest.idml"
definitions["globalPath"] = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/"

#ePub definitions
definitions["ePubTemplate"] = "/Volumes/Datos002/WESTPARK/iPray/epub/ePubTemplate/"

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/epub/"+month+"/"
definitions["appAndroidResult"] = "/Volumes/Datos002/WESTPARK/iPray/"+bookletName+"/AppAndroid/"
definitions["contentRoot"] = definitions["result"]+"OEBPS"
definitions["contentFile"] = definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     = definitions["contentRoot"]+"/toc.ncx"
definitions["finalCoverFile"]     = definitions["contentRoot"]+"/images/cover.jpeg"
definitions["finalLogoFile"]     = definitions["contentRoot"]+"/images/sub_cover.jpg"

definitions["textTemplate"] = definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

#months definitions
definitions["months"]  =  [month]
definitions["monthFigures"] = "10"
definitions["monthLimits"] = {}
definitions["monthLimits"][month] = {}
definitions["monthLimits"][month]["year"] = 2015
definitions["monthLimits"][month]["firstDay"] = 1
definitions["monthLimits"][month]["long"] = 31
definitions["monthLimits"][month]["firstWeekDay"] = 3

definitions["tableOfContentFile"] = definitions["contentRoot"] + "/text/tableOfContents.xhtml"
definitions["finalContentFile"] = definitions["contentRoot"] + "/text/content.xhtml"


### general definitions ###
definitions["bookletName"] = bookletName
definitions["bookletId"] = "iPray_"+bookletName+"_2015"
definitions["coverFile"]     = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/only_cover.jpg"
definitions["logoFile"]     = "/Volumes/Datos002/WESTPARK/iPray/"+month+"/sub_cover.jpg"

#idml
#idml.processIdmlLeaflet(definitions)

#ePub
#ePub.processEpubLeaflet(definitions)

#APP
appAndroid.processAndroidLeaflet(definitions)


