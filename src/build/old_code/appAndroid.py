from os import listdir
from os.path import isfile, join
import parse as p
import os
import shutil

import utils
from namesSpecs import *


def getCommentStylized(comment):
	content = ""
	for p in comment:
		content = content + "<p>"
		for b in p:
			if b[0] == 'normal':
				content = content + b[1]
			elif b[0] == 'italic':
				content = content + '<i>' + b[1] + '</i>'
			elif b[0] == 'boldItalic':
				content = content + '<b><i>' + b[1] + '</i></b>'
			elif b[0] == 'bold':
				content = content + '<b>' + b[1] + '</b>'
			else:
				print '''\n\n\n\n\n\nYo haven't considered this key (%s) for formating''' % b[0]
		content = content + "</p>\n"
	return content


def generateContent( leafletEntry, number):
	# header
	content =""

	content = content + "\t<div id=\"contentDay_"+str(number)+"\">\n"
	content = content + "\t<div class=\"space\" ></div>"
	content = content + "\t<div class=\"superday\">"+leafletEntry.day_string+' '+leafletEntry.month.upper()+"</div>"
	#content = content + "\t<div><div class=\"dayTittle\" >"+dayOfTheWeek+"</div>"

	if leafletEntry.saint != "":
		content = content  + "\t<div class=\"saintTittle\">"+leafletEntry.saint+"</div>\n"

	content = content  + "\t<div class=\"quote\"> "+leafletEntry.citation+"</div>\n"

	# gospel
	content = content  + "\t<div class=\"gospel\"><i>" +leafletEntry.gospel + "</i></div>\n"

	# comment
	subcontent = getCommentStylized(leafletEntry.comment)
	content = content + "\t<div>" + subcontent + "</div>\n</div>\n"
	return content


def fillXhtmlContents( definitions, leafletDays):

	intro = '''
	<?xml version="1.0" encoding="utf-8"?>
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
	  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

	<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
	  <title>Sometittle</title> <meta charset="UTF-8">
	  <link rel="stylesheet" href="stylesheet.css" type="text/css" />
	</head>
	<body>

	'''

	end = '''

	</body>
	</html>
	'''

	pageId = 0
	for ld in leafletDays :
		versionId = 0
		for v in ld.versions:
			# create html content
			dailyContent = generateContent(v, pageId)

			dailyContent = intro+dailyContent+end

			month_number =  monthNumber[definitions['language']][ld.month]

			#newFileContent = newFileContent + dailyContent
			if versionId == 0:
				fileName = definitions["appAndroidResult"]+"{day}-{month}.html".format( day=ld.day, month = month_number )
			else:
				fileName = definitions["appAndroidResult"]+"{day}-{month}_{id}.html".format( day=ld.day, month = month_number, id = versionId )


			extFile = open('./iPraybuild/openComa.txt', 'r')
			openComa = extFile.read()
			extFile.close()

			extFile = open('./iPraybuild/closeComa.txt', 'r')
			closeComa = extFile.read()
			extFile.close()

			dailyContent = dailyContent.replace(openComa, '\'')
			dailyContent = dailyContent.replace(closeComa, '\'')

			extFile = open(fileName, 'w')
			extFile.write(dailyContent)
			extFile.close()
			pageId = pageId+1
			versionId = versionId+1

	return pageId

def weekDayDef(idx):
	return weekDayNames[idx]

def composeDay(number, month):
	day = str(number)
	if number == 1 or (number%10==1 and number != 11):
		day = day + "st"
	elif number == 2 or (number%10==2 and number != 12):
		day = day + "nd"
	elif number == 3 or (number%10==3 and number != 13):
		day = day + "rd"
	else:
		day = day + "th"

	day = day + " " + month.upper()
	return day

def processAndroidLeaflet( definitions , leafletDays):

	if os.path.exists(definitions["appAndroidResult"]):
		shutil.rmtree(definitions["appAndroidResult"])

	os.mkdir(definitions["appAndroidResult"])

	pageId = fillXhtmlContents( definitions, leafletDays)

	print "Builded " + str(pageId) +" days!"
	print "congratulations: app files produced!!!"
