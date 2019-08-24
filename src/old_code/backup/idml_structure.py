from os import listdir
from os.path import isfile, join
import parse as p
import os
import shutil

import utils

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

def getTextContentToLoad(definitions ):
	textContents = []
	counter = 0
	for subdir in definitions["TEXT_SUBDIRS"] :
		Texts_dir = definitions["TEXT_GENERAL_DIR"]+subdir
		partfiles = [ g for g in listdir(Texts_dir) if isfile(join(Texts_dir,g)) ]
		for ff in partfiles :
			textContents.append(Texts_dir+ff)
			counter = counter+1

	return textContents

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
	return maxPage

def readContents(textContents, comments, gospel, citation, days, saints, definitions):
	textId = int(0)
	for text in textContents :
		extFile = open(text, 'r')
		items = {}
		for keyword, paragraphs in p.parse_text(str(extFile.read())) :
			items.update(p.PROCESSORS[keyword](paragraphs))
		extFile.close()

		#print text
		comments[textId] = items['COMMENTS']
		gospel[textId]   = items['GOSPEL']
		citation[textId] = items['CITATION']

		if not items.has_key('TITLE'):
			print "\n\n\n\nThere is no tittle!!!!"
			print text
			print items

		days[textId] = items['TITLE']
		if items['SUBTITLE'] == None:
			saints[textId] = ""
		else:
			saints[textId] = items['SUBTITLE']

		if items['TITLE'] == None:
			print "problemas con title en" + text
		if items['GOSPEL'] == None:
			print "problemas con title en" + text
		if items['CITATION'] == None:
			print "problemas con title en" + text
		if items['COMMENTS'] == None:
			print "problemas con title en" + text

		textId = textId+1

def fillContents( tabla, comments, gospel, 
				  citation, days, saints, 
				  maxPage, definitions):

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
	#Read the structure from the origin -> to fill later
	numOfPages = 70
	tabla = [{} for i in range(numOfPages)]
	used = [False for i in range(numOfPages)]
	
	textContents = getTextContentToLoad(definitions)

	maxPage = getPagesFromIdml(textContents, numOfPages, tabla, used, definitions)


	#read the content for filling
	comments = {}
	gospel = {}
	citation = {}
	days = {}
	saints = {}
	readContents(textContents, comments, gospel, citation, days, saints, definitions)

	print "DEBUG!!!!\n\n"
	print textContents[23]

	#Fill the the idml with the contents
	pageId = fillContents(  tabla, comments, gospel, 
				  			citation, days, saints, 
				  			maxPage, definitions )
	print "Builded " + str(pageId) +" pages!"

def getCommentStylized(comment):
	content = ""
	for p in comment:
		content = content + "<p>"
		for b in p:
			content = content + b[1]
		content = content + "</p>\n"
	return content


def generateContent(saint, day, citation, gospel, comment):
	# header
	content = "<div>\n"
	content = content  + "<div class=\"dayTittle\" >"+day+"</div>\n"
	if saint != "":
		content = content  + "<div class=\"saintTittle\"> - "+saint+"</div>\n"		
	content = content  + "<div class=\"quote\"> "+citation+"</div>\n"

	# gospel
	content = content  + "<p class=\"gospel\"><i>" + gospel + "</i></p>"

	# comment
	subcontent = getCommentStylized(comment)
	content = content + subcontent + "</div>"
	return content


def fillXhtmlContents( comments, gospel, 
				  	   citation, days, saints, 
				       definitions):

	textFolder = definitions["contentRoot"] +"/text/"

	pageId = 0
	fileNames =[]
	for i in range(len(comments)) :
		if i > definitions["TEXTS_NUM"]:
			continue

		# create html content
		content = generateContent(saints[pageId], days[pageId], citation[pageId], gospel[pageId], comments[pageId])

		# read template
		fileName = "iPrayDay0%s.xhtml" % i
		shutil.copyfile(definitions["textTemplate"], textFolder+fileName)
		print "Created file: " + textFolder+fileName

		extFile = open(textFolder+fileName, 'r')
		fileContent = str(extFile.read())
		extFile.close()

		# put new content
		tittleTag = "iPrayTittle"
		contentTag = "iPrayContent"

		contentPos = fileContent.find(contentTag)
		tittlePos = fileContent.find(tittleTag)

		newFileContent = fileContent[:tittlePos] + days[pageId]
		newFileContent = newFileContent + fileContent[tittlePos+len(tittleTag):contentPos]
		newFileContent = newFileContent + content
		newFileContent = newFileContent + fileContent[contentPos+len(contentTag):]
		pageId = pageId+1

		# save file
		extFile = open(textFolder+fileName, 'w')
		extFile.write(newFileContent)
		extFile.close()

		fileNames.append(fileName)

	return pageId, fileNames

def createIndexAndStructure(fileNames, days, definitions):

	# Content file
	contentFile = open(definitions["contentFile"], 'r')
	fileContent = str(contentFile.read())
	contentFile.close()	

	tittleKey = "TitleiPrayBook"
	idKey = "iPrayBookletId"
	contentsKey = "iPrayContentsTemplate"
	structureKey = "iPrayStructureTemplate"

	
	tittlePos = (fileContent.find(tittleKey))
	idPos = (fileContent.find(idKey))
	contentsPos = (fileContent.find(contentsKey))
	structurePos = (fileContent.find(structureKey))

	pos = 0
	block1  = fileContent[pos:tittlePos]
	pos = tittlePos + len(tittleKey)
	block2 = fileContent[pos:idPos]
	pos = idPos + len(idKey)
	block3 = fileContent[pos:contentsPos]
	pos = contentsPos + len(contentsKey)
	block4 = fileContent[pos:structurePos]
	pos = structurePos + len(structureKey)
	block5  = fileContent[pos:]

	newFileContent = block1 + definitions["bookletName"]
	newFileContent = newFileContent + block2 + definitions["bookletId"]

	subfolder = "Text"

	# create file references
	filesReferences = ""
	for f in fileNames:
		filesReferences = filesReferences +("\t<item id=\""+f+"\" href=\""+subfolder+"/"+f+"\" media-type=\"application/xhtml+xml\"/>\n")

	# create file structure
	filesStructure = ""
	for f in fileNames:
		filesStructure = filesStructure +("\t<itemref idref=\""+f+"\"/>\n")

	newFileContent = newFileContent + block3 + filesReferences + block4 + filesStructure + block5

	contentFile = open(definitions["contentFile"], 'w')
	contentFile.write(newFileContent)
	contentFile.close()

	#toc - navigation references
	contentFile = open(definitions["tocFile"], 'r')
	fileContent = str(contentFile.read())
	contentFile.close()	

	idKey = "iPrayBookletId"
	navigationKey = "navigationTemplate"

	idPos = (fileContent.find(idKey))
	navigationPos = (fileContent.find(navigationKey))

	pos = 0
	block1  = fileContent[pos:idPos]
	pos = idPos + len(idKey)
	block2 = fileContent[pos:navigationPos]
	pos = navigationPos + len(navigationKey)
	block3 = fileContent[pos:]

	counter = 0
	nav = ""
	for f in fileNames:
		nav = nav + "\t<navPoint id=\"navPoint-"+str(counter+5)+"\" playOrder="+str(counter+5)+">\n"
		nav = nav + "\t\t<navLabel>\n"
		nav = nav + "\t\t\t<text>"+days[counter]+"</text>\n"
		nav = nav + "\t\t</navLabel>\n"
		nav = nav + "\t\t<content src="+subfolder+"/"+f+"/>\n"
		nav = nav + "\t</navPoint>\n"
		counter = counter+1

	newFileContent = block1+definitions["bookletName"]+block2+nav+block3

	contentFile = open(definitions["tocFile"], 'w')
	contentFile.write(newFileContent)
	contentFile.close()

	
def processEpubLeaflet( definitions ):

	if os.path.exists(definitions["result"]):
		shutil.rmtree(definitions["result"])
	
	os.mkdir(definitions["result"])

	utils.copyDirectory(definitions["ePubTemplate"],definitions["result"])

	#read the content for filling
	comments = {}
	gospel = {}
	citation = {}
	days = {}
	saints = {}
	textContents = getTextContentToLoad(definitions)
	readContents(textContents, comments, gospel, citation, days, saints, definitions)

	#Fill the the idml with the contents
	pageId, fileNames = fillXhtmlContents( comments, gospel, 
				  						citation, days, saints, 
				  						definitions )

	print "Builded " + str(pageId) +" pages!"

	createIndexAndStructure(fileNames, days, definitions)

	#compress the set as an ePub File
	utils.zip_tree(definitions["result"], definitions["result"][:len(definitions["result"])-1]+".ePub")
	shutil.rmtree(definitions["result"])

	print "congratulations: ePub finished!!!"


