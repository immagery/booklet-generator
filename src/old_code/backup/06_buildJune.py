import idml
import ePub


# idml definitions
definitions = {}
definitions["mypath"] = "/Volumes/Datos002/WESTPARK/iPray/june/deployment/orig/Stories/"
definitions["outPath"] = "/Volumes/Datos002/WESTPARK/iPray/june/deployment/dest/Stories/"

definitions["TEXTS_NUM"] = 37
definitions["TEXT_GENERAL_DIR"] = "/Users/chus/Dropbox/3plus2/3plus2_text/Summer_term"
definitions["TEXT_SUBDIRS"] = ["/May/","/June/"]

definitions["inFile"] = "june_orig.idml"
definitions["outFile"] = "june_dest.idml"
definitions["globalPath"] = "/Volumes/Datos002/WESTPARK/iPray/june/"

#ePub definitions
definitions["ePubTemplate"] = "/Volumes/Datos002/WESTPARK/iPray/epub/ePubTemplate/"

definitions["result"] = "/Volumes/Datos002/WESTPARK/iPray/epub/june/"
definitions["contentRoot"] = definitions["result"]+"OEBPS"
definitions["contentFile"] = definitions["contentRoot"]+"/content.opf"
definitions["tocFile"]     = definitions["contentRoot"]+"/toc.ncx"

definitions["textTemplate"] = definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

### general definitions ###

definitions["bookletName"] = "June"
definitions["bookletId"] = "iPray_June_2015"
definitions["coverFile"] = "/Volumes/Datos002/WESTPARK/iPray/june/june_leaflet_cover_hi.jpg"

#idml
#idml.processIdmlLeaflet(definitions)

#ePub
ePub.processEpubLeaflet(definitions)



