import idml
import ePub


# idml definitions
definitions = {}
definitions["mypath"] = "/Volumes/Datos002/WESTPARK/iPray/july/deployment/orig/Stories/"
definitions["outPath"] = "/Volumes/Datos002/WESTPARK/iPray/july/deployment/dest/Stories/"

definitions["TEXTS_NUM"] = 31
definitions["TEXT_GENERAL_DIR"] = "/Users/chus/Dropbox/3plus2/3plus2_text"
definitions["TEXT_SUBDIRS"] = ["/07_july/"]

definitions["inFile"] = "july_orig.idml"
definitions["outFile"] = "july_dest.idml"
definitions["globalPath"] = "/Volumes/Datos002/WESTPARK/iPray/july/"

#ePub definitions
definitions["ePubTemplate"] = "/Volumes/Datos002/WESTPARK/iPray/epub/ePubTemplate/"

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/epub/july/"
definitions["contentRoot"] = definitions["result"]+"OEBPS"
definitions["contentFile"] = definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     = definitions["contentRoot"]+"/toc.ncx"
definitions["finalCoverFile"]     = definitions["contentRoot"]+"/images/cover.jpeg"
definitions["finalLogoFile"]     = definitions["contentRoot"]+"/images/sub_cover.jpg"

definitions["textTemplate"] = definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

definitions["months"]  =  ["july"]
definitions["monthLimits"] = {}
definitions["monthLimits"]["july"] = {}
definitions["monthLimits"]["july"]["year"] = 2015
definitions["monthLimits"]["july"]["firstDay"] = 1
definitions["monthLimits"]["july"]["long"] = 31
definitions["monthLimits"]["july"]["firstWeekDay"] = 2

definitions["tableOfContentFile"] = definitions["contentRoot"] + "/text/tableOfContents.xhtml"
definitions["finalContentFile"] = definitions["contentRoot"] + "/text/content.xhtml"


### general definitions ###
definitions["bookletName"] = "July"
definitions["bookletId"] = "iPray_July_2015"
definitions["coverFile"]     = "/Volumes/Datos002/WESTPARK/iPray/July/only_cover.jpg"
definitions["logoFile"]     = "/Volumes/Datos002/WESTPARK/iPray/July/sub_cover.jpg"

#idml
#idml.processIdmlLeaflet(definitions)

#ePub
ePub.processEpubLeaflet(definitions)



