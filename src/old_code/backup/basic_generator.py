from os import listdir
from os.path import isfile, join
import parse as p
import os
import shutil

import utils

def readContents(textContents, comments, gospel, citation, days, saints, definitions):
	textId = int(0)
	for text in textContents :
		if not text.endswith(".txt"):
			continue

		extFile = open(text, 'r')
		items = {}
		for keyword, paragraphs in p.parse_text(str(extFile.read())) :
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

