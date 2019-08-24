from os import listdir
from os.path import isfile, join

import parse as p
import os
import shutil

import basic_generator as gen
import utils

import zipfile
import re
import copy

def setContent(inCitFileName, outCitFileName, content):
	inCitFile  = open(inCitFileName, 'r')
	outCitFile = open(outCitFileName, 'w')

	inText = inCitFile.read()

	idx1 = inText.find("codigo")

	if idx1 >= 0:
		firstText = inText[0:idx1]
		secondText = inText[idx1+10:]
		inText = firstText+content+secondText

	outCitFile.write(inText)

	inCitFile.close()
	outCitFile.close()

def setMainContent(inCitFileName, outCitFileName, gospelText, commentsText):
	inCitFile  = open(inCitFileName, 'r')
	outCitFile = open(outCitFileName, 'w')

	#read the origin
	iniBlock = 6
	midBlock = 5
	finBlock = 3
	inTextIni = ""
	for f in range(iniBlock) :
		inTextIni = inTextIni + inCitFile.readline()

	for f in range(midBlock) :
		inCitFile.readline()

	inTextFin = ""
	for f in range(finBlock) :
		inTextFin = inTextFin + inCitFile.readline()

	content = ""

	gospelContent = paragraphStyleBlock("cita", characterStyleBlock("contenido_cita", gospelText, True))#+"\t\t\t\t</br>\n")
	content = content + gospelContent

	for parr in range(len(commentsText)) :
		textParrafo = ""
		elementParrafo = commentsText[parr]
		for block in range(len(elementParrafo)) :
			elementBlock = elementParrafo[block]
			if block == len(elementParrafo)-1 and parr != len(commentsText)-1: 
				textParrafo = textParrafo + characterStyleBlock(elementBlock[0], elementBlock[1], True)
			else:
				textParrafo = textParrafo + characterStyleBlock(elementBlock[0], elementBlock[1])

		content = content + paragraphStyleBlock("normal",textParrafo)


	finalText = inTextIni+content+inTextFin

	outCitFile.write(finalText)

	inCitFile.close()
	outCitFile.close()

def characterStyleBlock(style, content, withspace = False):
	ini = """\t\t\t\t<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/{0}">
			 \t\t<Content>""".format(style)
	fin = """</Content>\n"""
	if withspace : fin = fin + "\t\t\t\t<Br />\n"
	fin = fin + "\t\t\t\t</CharacterStyleRange>\n"
	return ini+content+fin

def paragraphStyleBlock(style, content):
	ini = """\t\t\t<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{0}">\n""".format(style)
	fin = "\t\t\t</ParagraphStyleRange>\n"
	return ini+content+fin

def getPagesFromIdml(textContents, numOfPages, tabla, used, definitions ):

	allfiles = [ f for f in listdir(definitions["mypath"]) if isfile(join(definitions["mypath"],f)) ]

	# 1. Read all the stories files and create the relation table
	minPage = int(9999)
	maxPage = int(-1)
	print "procesando fichero imdl"
	for f in range(len(allfiles)) :
		storyFile = open(definitions["mypath"]+allfiles[f], 'r')
		#print definitions["mypath"]+allfiles[f]
		text = storyFile.read()
		pos = text.find("codigo")
		
		if pos < 0 : continue
		pagina = text[pos+6:pos+9]
		bloque = text[pos+9:pos+10]
		
		#print "pagina " + str(pagina) + " y bloque " + str(bloque) + " file " + allfiles[f]

		value = int(pagina)

		tabla[value][bloque] = allfiles[f]
		used[value] = True
		if value > maxPage : 
			maxPage = int(pagina)
		if value < minPage : 
			minPage = int(pagina)
		
		#print allfiles[f] + "- pagina: " + pagina + " - bloque: " + bloque

	#print "minPage " + str(minPage)
	#print "maxPage " + str(maxPage)
	#print "textContents " + str(len(textContents))
	return maxPage,minPage

def fillContents( tabla, comments, gospel, 
				  citation, days, saints, 
				  maxPage, minPage, definitions):

	maxPage = int(maxPage)
	pageId = 0
	print "insertando contenido en fichero idml"
	for i in range(len(comments)) :
		if i > definitions["TEXTS_NUM"]:
			continue

		tablaId = i + minPage
		
		if not tabla[tablaId].has_key('C'):
			print "No esta bien definida la C de la pagina " + str(tablaId)
		if not tabla[tablaId].has_key('D'):
			print "No esta bien definida la D de la pagina " + str(tablaId)
		if not tabla[tablaId].has_key('S'):
			print "No esta bien definida la S de la pagina " + str(tablaId)
		if not tabla[tablaId].has_key('T'):
			print "No esta bien definida la T de la pagina " + str(tablaId)

		if 'C' not in tabla[tablaId].keys():
			print tablaId, tabla[tablaId]

		#citation
		inCitFileName = definitions["mypath"]+tabla[tablaId]['C']
		outCitFileName = definitions["outPath"]+tabla[tablaId]['C']
		setContent(inCitFileName, outCitFileName, citation[pageId])
		
		#day
		inCitFileName = definitions["mypath"]+tabla[tablaId]['D']
		outCitFileName = definitions["outPath"]+tabla[tablaId]['D']
		setContent(inCitFileName, outCitFileName, days[pageId])

		#saint
		inCitFileName = definitions["mypath"]+tabla[tablaId]['S']
		outCitFileName = definitions["outPath"]+tabla[tablaId]['S']
		setContent(inCitFileName, outCitFileName, saints[pageId])

		#gospel+comments
		inCitFileName = definitions["mypath"]+tabla[tablaId]['T']
		outCitFileName = definitions["outPath"]+tabla[tablaId]['T']
		setMainContent(inCitFileName, outCitFileName, gospel[pageId], comments[pageId])
		pageId = pageId+1

	return pageId


def processIdmlLeaflet( definitions ):
	#Create folders and temp files
	tempDir = definitions["globalPath"] + "deployment"
	origDir = tempDir+"/orig"
	destDir = tempDir+"/dest"

	tempDir = definitions["globalPath"] + "deployment"

	if not os.path.exists(tempDir):
		os.mkdir(tempDir)

	if os.path.exists(origDir):
		shutil.rmtree(origDir)

	if os.path.exists(destDir):
		shutil.rmtree(destDir)

	os.mkdir(origDir)
	os.mkdir(destDir)

	zipInterface = zipfile.ZipFile(definitions["globalPath"]+definitions["inFile"], 'r')
	zipInterface.extractall(origDir)
	zipInterface.extractall(destDir)
	zipInterface.close()

	#Read the structure from the origin -> to fill later
	numOfPages = 70
	tabla = [{} for i in range(numOfPages)]
	used = [False for i in range(numOfPages)]
	
	textContents = gen.getTextContentToLoad(definitions)

	maxPage, minPage = getPagesFromIdml(textContents, numOfPages, tabla, used, definitions)

	#read the content for filling
	comments = {}
	gospel = {}
	citation = {}
	days = {}
	saints = {}
	gen.readContents(textContents, comments, gospel, citation, days, saints, definitions)


	#Fill the the idml with the contents
	pageId = fillContents(  tabla, comments, gospel, 
				  			citation, days, saints, 
				  			maxPage, minPage, definitions )

	print "Builded " + str(pageId) +" pages!"

	#Create final result and 
	#delete folders and temp files
	utils.zip_tree(destDir, definitions["globalPath"] + definitions["outFile"])
	shutil.rmtree(tempDir)

