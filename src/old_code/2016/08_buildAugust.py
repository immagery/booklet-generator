import idml
import ePub


# idml definitions
definitions = {}
definitions["mypath"] = "/Volumes/Datos002/WESTPARK/iPray/august/deployment/orig/Stories/"
definitions["outPath"] = "/Volumes/Datos002/WESTPARK/iPray/august/deployment/dest/Stories/"

definitions["TEXTS_NUM"] = 31
definitions["TEXT_GENERAL_DIR"] = "/Users/chus/Dropbox/3plus2/3plus2_text"
definitions["TEXT_SUBDIRS"] = ["/08_August/"]

definitions["inFile"] = "august_orig.idml"
definitions["outFile"] = "august_dest.idml"
definitions["globalPath"] = "/Volumes/Datos002/WESTPARK/iPray/august/"

#ePub definitions
definitions["ePubTemplate"] = "/Volumes/Datos002/WESTPARK/iPray/epub/ePubTemplate/"

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/epub/august/"
definitions["contentRoot"] = definitions["result"]+"OEBPS"
definitions["contentFile"] = definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     = definitions["contentRoot"]+"/toc.ncx"
definitions["finalCoverFile"]     = definitions["contentRoot"]+"/images/cover.jpeg"
definitions["finalLogoFile"]     = definitions["contentRoot"]+"/images/sub_cover.jpg"

definitions["textTemplate"] = definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

definitions["months"]  =  ["august"]
definitions["monthLimits"] = {}
definitions["monthLimits"]["august"] = {}
definitions["monthLimits"]["august"]["year"] = 2015
definitions["monthLimits"]["august"]["firstDay"] = 1
definitions["monthLimits"]["august"]["long"] = 31
definitions["monthLimits"]["august"]["firstWeekDay"] = 5

definitions["tableOfContentFile"] = definitions["contentRoot"] + "/text/tableOfContents.xhtml"
definitions["finalContentFile"] = definitions["contentRoot"] + "/text/content.xhtml"


### general definitions ###
definitions["bookletName"] = "August"
definitions["bookletId"] = "iPray_August_2015"
definitions["coverFile"]     = "/Volumes/Datos002/WESTPARK/iPray/August/only_cover.jpg"
definitions["logoFile"]     = "/Volumes/Datos002/WESTPARK/iPray/August/sub_cover.jpg"

#idml
idml.processIdmlLeaflet(definitions)

#ePub
#ePub.processEpubLeaflet(definitions)



