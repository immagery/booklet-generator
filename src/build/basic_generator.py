from os import listdir
from os.path import isfile, join
import parse as p
import os
import shutil
import io
import codecs 

import utils

from namesSpecs import *

def readContent(folder, textFile):
	if not textFile.endswith(".txt"):
		raise Exception('The file %s is not a txt file' % textFile)

	extFile = open(folder+textFile, 'r')

	entry = dayObj()

	### get classification

	if 'week' in textFile:
		classification = textFile.split(' ')

		if len(classification) < 4:
			raise Exception('The file %s doesnt define the season properly' % textFile)

		seasonName = textFile.split("week")[1].split(".txt")[0].strip()

		if seasonName == '':
			raise Exception('The season %s is not properly defined in the file %s' % (seasonName, textFile))

		entry.season = seasonName

		week_count = 0
		for id in range(len(classification)):
			if classification[id].lower() == "week":
				week_count = id

		entry.seasonWeek = int(''.join([i for i in classification[week_count-1] if i.isdigit()]))
		entry.seasonWeekday = classification[week_count-2]

		if entry.seasonWeekday == 'Sunday':
			if len(classification) > 4:
				entry.cycle = classification[4].upper()

			else:
				entry.cycle = None

	else:
		if '(' not in textFile or ')' not in textFile:
			entry.area = 'All'
		else:
			entry.area = textFile.split('(')[1].split(')')[0]

		entry.season = None

	items = {}
	for keyword, paragraphs in p.parse_text(str(extFile.read())) :
		items.update(p.PROCESSORS[keyword](paragraphs))
	extFile.close()

	### Check items
	if not "COMMENTS" in items.keys():
		raise Exception('no COMMENTS in %s!' % textFile)

	if not "GOSPEL" in items.keys():
		raise Exception('no GOSPEL in %s!' % textFile)

	if not "CITATION" in items.keys():
		raise Exception('no CITATION in %s!' % textFile)


	entry.comment  = items['COMMENTS']
	entry.gospel   = items['GOSPEL']
	entry.citation = items['CITATION']

	if not items.has_key('TITLE'):
		# looking for the tittle manually
		fileOpened = codecs.open(folder+textFile, 'r', 'utf-8-sig')
		line = fileOpened.readline()
		firstBlock = line.find('TITLE:')
		secondBlock = line.find('(')
		thirdBlock = line.find(')')


		title = line[firstBlock+6:secondBlock]
		secondTitle = line[secondBlock+1:thirdBlock]

		items['TITLE'] = title

		if(secondBlock > 0):	
			items['SUBTITLE'] = secondTitle
		else:
			items['SUBTITLE'] = ""

		fileOpened.close()


	title = items['TITLE']
	if items['SUBTITLE'] == None:
		entry.saint = ""
	else:
		entry.saint = items['SUBTITLE']

	titleAux = title.split(' ')
	title = [t for t in titleAux if t is not u'']
	if len(title) < 3:
		raise Exception('The file %s doesnt define the day properly' % textFile)

	entry.day_string = title[1]
	entry.day_number = int(''.join([i for i in title[1] if i.isdigit()]))
	entry.month = title[2].split('\r')[0]

	if items['TITLE'] == None:
		Exception("problemas con title en" + textFile)
	if items['GOSPEL'] == None:
		Exception("problemas con title en" + textFile)
	if items['CITATION'] == None:
		Exception("problemas con title en" + textFile)
	if items['COMMENTS'] == None:
		Exception("problemas con title en" + textFile)

	return entry



def readContents(textContents, comments, gospel, citation, days, saints, definitions):
	textId = int(0)
	for text in textContents :
		if not text.endswith(".txt"):
			continue

		extFile = open(text, 'r')
		items = {}
		for keyword, paragraphs in p.parse_text(str(extFile.read())) :
			#print text
			items.update(p.PROCESSORS[keyword](paragraphs))
		extFile.close()

		if not "COMMENTS" in items.keys():
			print "no COMMENTS!"
			print text
			return

		if not "GOSPEL" in items.keys():
			print "no GOSPEL!"
			print text
			return

		if not "CITATION" in items.keys():
			print "no CITATION!"
			print text
			return

		#print text
		comments[textId] = items['COMMENTS']
		gospel[textId]   = items['GOSPEL']
		citation[textId] = items['CITATION']

		#print items.keys()

		if not items.has_key('TITLE'):
			#print "\n\n\n\nThere is no tittle!!!!"
			#print text
			#print items
			#return
			#print "looking for a tittle"
			fileOpened = open(text, 'r')
			line = fileOpened.readline()
			firstBlock = line.find('TITLE:')
			secondBlock = line.find('(')
			thirdBlock = line.find(')')
			#print firstBlock, secondBlock, thirdBlock

			title = line[firstBlock+6:secondBlock]
			secondTitle = line[secondBlock+1:thirdBlock]

			items['TITLE'] = title

			if(secondBlock > 0):
				items['SUBTITLE'] = secondTitle
			else:
				items['SUBTITLE'] = ""

			#print items['TITLE'], items['SUBTITLE']

			fileOpened.close()


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

def getTextContentToLoad(definitions ):
	textContents = []
	counter = 0
	for subdir in definitions["TEXT_SUBDIRS"] :
		Texts_dir = definitions["TEXT_GENERAL_DIR"]+subdir
		partfiles = [ g for g in listdir(Texts_dir) if isfile(join(Texts_dir,g)) ]
		for ff in partfiles :
			if 'txt' in ff:
				textContents.append(Texts_dir+ff)
				counter = counter+1
	print len(textContents)

	return textContents
'''
def defineSpecificVariables(definitions, baseProcessDirectory):

	######################
	# idml definitions
	######################
	definitions["inFile"] 		= definitions["codeName"]+"_orig.idml"
	definitions["outFile"] 		= definitions["codeName"]+"_dest.idml"
	definitions["mypath"]  		= definitions["globalPath"]+"/deployment/orig/Stories/"
	definitions["outPath"] 		= definitions["globalPath"]+"/deployment/dest/Stories/"

	######################
	#ePub definitions
	######################
	definitions["ePubTemplate"] 		= baseProcessDirectory+"/epub/ePubTemplate/"

	definitions["result"] 				= definitions["globalPath"]+"ePub/"
	definitions["contentRoot"] 			= definitions["result"]     +"OEBPS"
	definitions["contentFile"] 			= definitions["contentRoot"]+"/content.opf"
	definitions["tocFile"]     			= definitions["contentRoot"]+"/toc.ncx"
	definitions["finalCoverFile"]   	= definitions["contentRoot"]+"/images/cover.jpeg"
	definitions["finalLogoFile"]    	= definitions["contentRoot"]+"/images/sub_cover.jpg"

	definitions["textTemplate"] 		= definitions["ePubTemplate"] + "OEBPS/text/dayTemplate.xhtml"

	definitions["tableOfContentFile"] 	= definitions["contentRoot"] + "/text/tableOfContents.xhtml"
	definitions["finalContentFile"] 	= definitions["contentRoot"] + "/text/content.xhtml"

	definitions["mobiStyleFile"] 		= baseProcessDirectory+"/epub/mobiStyleTemplate.css"
	definitions["mobiStyleFileDestination"] = "/OEBPS/Styles/Stylesheet.css"

	definitions["coverFile"]    		= definitions["globalPath"]+"/cover_mid.jpg"
	definitions["logoFile"]     		= definitions["globalPath"]+"/cover_in_advent.jpg"

	######################
	# android definitions
	######################
	definitions["appAndroidResult"] 	= definitions["globalPath"]+"/AppAndroid/"
'''