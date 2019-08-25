from os import listdir
from os.path import isfile, join
import parse as p
import os
import shutil

import utils

import calendar
from namesSpecs import *

import codecs 

def getCommentStylized(comment):
	content = ""
	for p in comment:
		content = content + "<p>"
		for b in p:
			bcont = b[1]
			if b[0] == 'italic':
				bcont = '<i>'+bcont+'</i>'
			if b[0] == 'bold':
				bcont = '<b>'+bcont+'</b>'
			if b[0] == 'boldItalic':
				bcont = '<b><i>'+bcont+'</i></b>'

			content = content + bcont
		content = content + "</p>\n"


	return content


def generateContent(dayData):
	# heade
	content = ""
	#if dayData.link == None:
	#	content = content + "\t<div id=\"nothing\">\n"
	#else:
	content = content + "\t<a id=\"contentDay_"+str(dayData.day_number)+"\"></a>\n"
	content = content + "\t<div class=\"space\" ></div>"
	content = content + "\t<div class=\"superday\">"+dayData.day_string
	content = content + "<a class=\"back_cal\" href=\"tableOfContents.xhtml\"> [calendar]</a></div>"
	#content = content + "\t<div><div class=\"dayTittle\" >"+dayOfTheWeek+"</div>"
	if dayData.saint != "":
		content = content  + "\t<div class=\"saintTittle\">"+ codecs.decode(dayData.saint, 'utf-8-sig') +"</div>\n"

	content = content  + "\t<div class=\"qpuote\"> "+ codecs.decode(dayData.citation, 'utf-8-sig') +"</div>\n"

	# gospel
	content = content  + "\t<div class=\"gospel\">" + codecs.decode(dayData.gospel, 'utf-8-sig') + "</div>\n"

	# comment
	subcontent = getCommentStylized(dayData.comment)
	content = content + "\t<div>" + codecs.decode(subcontent, 'utf-8-sig') + "</div>\n"
	return content


def fillXhtmlContents( definitions, leafletDays):

	# read template
	extFile = open(definitions["finalContentFile"], 'r')
	fileContent = str(extFile.read())
	extFile.close()

	# put new content
	tittleTag = "iPrayTittle"
	contentTag = "iPrayContent"

	contentPos = fileContent.find(contentTag)
	tittlePos = fileContent.find(tittleTag)

	newFileContent = fileContent[:tittlePos]
	newFileContent = newFileContent + definitions["bookletName"]
	newFileContent = newFileContent + fileContent[tittlePos + len(tittleTag):contentPos]

	monthDay =0
	pageId = 0
	newFileContent += "\t<hr/>"
	for lday in leafletDays :
		# create html content
		print lday, [ v.link for v in lday.versions]
		for v in lday.versions:
			dailyContent = generateContent(v)
			newFileContent = newFileContent + dailyContent
			pageId +=1

	newFileContent = newFileContent + fileContent[contentPos+len(contentTag):]

	# save file
	extFile = codecs.open(definitions["finalContentFile"], 'w', encoding='utf-8-sig')#open(definitions["finalContentFile"], 'w')
	extFile.write(newFileContent)
	extFile.close()

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

def findInLeaflet(day, month, year, leafletDays):
	for ld in leafletDays:
		if ld.day == day and ld.month == month and ld.year == year:
			return ld

	return None


def buildMonthHTML(month, year, leafletDays, language = "english"):

	## init
	monthTable = "<div>\n"
	monthTable = monthTable + "<div id=\"evcal_head_%s\" class=\"calendar_header \">\n" % month
	monthTable = monthTable + "<p id=\"evcal_cur_%s\">" % month + month.upper() + " " + str(year) + "</p>\n"
	monthTable = monthTable + "</div>\n"
	monthTable = monthTable + "<div class=\"eventon_fullcal\" >\n"
	monthTable = monthTable + "<div>\n"
	monthTable = monthTable + "<div class=\"evofc_month\" >\n"
	monthTable = monthTable + "<div class=\"eventon_fc_daynames\" >\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >mon</p>\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >tue</p>\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >wed</p>\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >thu</p>\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >fri</p>\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >sat</p>\n"
	monthTable = monthTable + "<p class=\"evo_fc_day\" >sun</p>\n"
	monthTable = monthTable + "<div class=\"clear\" ></div>\n"
	monthTable = monthTable + "</div>\n"
	monthTable = monthTable + "<div class=\"eventon_fc_days\" >\n"

	monthInt = monthNumber[language][month]

	cal = calendar.Calendar()
	numberIdx = 0
	for week in cal.monthdatescalendar(year,monthInt):
		for weekDay in week:
			#link = findInLeaflet(weekDay.day, monthNames[weekDay.month], weekDay.year, leafletDays)
			if weekDay.month != monthInt:
				monthTable = monthTable + "<p class=\"evo_fc_day on_focus\" >"+str(weekDay.day)+"</p>\n"
			else:
				#if link:
				## normal
				generatedLink = ""
				#if link.versions and len(link.versions)>0:
				generatedLink = weekDay.day
				#link.versions[0].getUniqueLink()
				#link.versions[0].link= "contentDay_"+str(generatedLink)

				monthTable = monthTable + "<p class=\"evo_fc_day\" ><a href=\"content.xhtml#contentDay_"+str(generatedLink)+"\">"+str(weekDay.day)+"</a></p>\n"
				numberIdx = numberIdx + 1

			#else:
			#	print 'no link'
			#	monthTable = monthTable + "<p class=\"evo_fc_day\" >"+str(weekDay.day)+"</p>\n"



	## end
	monthTable = monthTable + "<div class=\"clear\"></div>\n"
	monthTable = monthTable + "</div>\n"
	monthTable = monthTable + "</div>\n"
	monthTable = monthTable + "</div>\n"
	monthTable = monthTable + "<div class=\"clear\"></div>\n"
	monthTable = monthTable + "</div>\n"
	monthTable = monthTable + "<div class=\"clear\"></div>\n"
	monthTable = monthTable + "</div>\n"

	return monthTable


def createIndexAndStructure(definitions, leafletDays, month, year, language):

	#We only need to create the indices file

	# Content file
	contentFile = open(definitions["contentFile"], 'r')
	fileContent = str(contentFile.read())
	contentFile.close()

	tittleKey = "TitleiPrayBook"
	idKey = "iPrayBookletId"

	tittlePos = (fileContent.find(tittleKey))
	idPos = (fileContent.find(idKey))

	pos = 0
	block1  = fileContent[pos:tittlePos]
	pos = tittlePos + len(tittleKey)
	block2 = fileContent[pos:idPos]
	pos = idPos + len(idKey)
	block5  = fileContent[pos:]

	newFileContent = block1 + definitions["bookletName"]
	newFileContent = newFileContent + block2 + definitions["bookletId"]
	newFileContent = newFileContent + block5

	contentFile = open(definitions["contentFile"], 'w')
	contentFile.write(newFileContent)
	contentFile.close()

	# toc file - changing id
	contentFile = open(definitions["tocFile"], 'r')
	fileContent = str(contentFile.read())
	contentFile.close()

	idPos = (fileContent.find(idKey))
	newFileContent = fileContent[:idPos] + definitions["bookletId"] + fileContent[idPos + len(idKey):]

	contentFile = open(definitions["tocFile"], 'w')
	contentFile.write(newFileContent)
	contentFile.close()

	#table of contents
	contentFile = open(definitions["tableOfContentFile"], 'r')
	fileContent = str(contentFile.read())
	contentFile.close()
	idKey = "iPrayTableOfContents"
	idPos = (fileContent.find(idKey))

	pos = 0
	block1  = fileContent[pos:idPos]
	pos = idPos + len(idKey)
	block3 = fileContent[pos:]

	numberIdx = 1
	counter = 0
	tableOfContexts = ""

	'''
	months = {}
	for entry in leafletDays:
		if entry.versions and len(entry.versions) > 0:
			year = entry.versions[0].year
			if year not in months.keys():
				months[year] = []
			month = entry.versions[0].month
			if month not in months[year]:
				months[year].append(month)

	for year, monthList in months.items():
		for m in monthList:
			mHTML = buildMonthHTML(m, year, leafletDays)
			tableOfContexts = tableOfContexts + mHTML
	'''

	mHTML = buildMonthHTML(month, year, leafletDays, language)
	tableOfContexts = tableOfContexts + mHTML

  	# link to other contents
  	linksMoreContents = "<div><h3><a href=\"commonPrayers.xhtml\">Common Prayers</a></h3></div>"

	newFileContent = block1+tableOfContexts+linksMoreContents+block3

	tempFile = definitions["tableOfContentFile"]
	contentFile = open(tempFile, 'w')
	contentFile.write(newFileContent)
	contentFile.close()

def processEpubLeaflet( definitions, leafletDays ):

	if os.path.exists(definitions["result"]):
		shutil.rmtree(definitions["result"])

	os.mkdir(definitions["result"])

	utils.copyDirectory(definitions["ePubTemplate"] , definitions["result"])
	createIndexAndStructure(definitions, leafletDays, definitions['firstMonth'], definitions['firstYear'], definitions['language'])


	#Fill the structure with the contents
	pageId = fillXhtmlContents( definitions, leafletDays)

	print "ePub Builded " + str(pageId) +" pages!"

	# copy the right cover
	#print definitions["coverFile"],definitions["finalCoverFile"]
	shutil.copyfile(definitions["coverFile"],definitions["finalCoverFile"])
	shutil.copyfile(definitions["logoFile"],definitions["finalLogoFile"])

	basePath = definitions["result"][:len(definitions["result"])-1]
	leafletPath = basePath[:basePath.rfind('/')+1]

	#print leafletPath

	#compress the set as an ePub File
	utils.zip_tree(definitions["result"], leafletPath+definitions["bookletId"]+".epub")
	#shutil.rmtree(definitions["result"])

	# generate epub for mobi
	pathForMobi = definitions["result"][:len(definitions["result"])-1]+"_forMobi/"
	if os.path.exists(pathForMobi):
		shutil.rmtree(pathForMobi)

	os.mkdir(pathForMobi)

	utils.copyDirectory(definitions["result"], pathForMobi)

	# copy the right styleSheet
	shutil.copyfile(definitions["mobiStyleFile"], pathForMobi+definitions["mobiStyleFileDestination"])

	#compress the set as an ePub File
	utils.zip_tree(definitions["result"], leafletPath+definitions["bookletId"]+"_forMobi.epub")
	#shutil.rmtree(definitions["result"])

	print "congratulations: ePub ready for conversion to mobi!!!"


def build_epub (*args, **kargs) :
	printf("Build epub!!!!")

def build_mobi (*args, **kargs) :
	printf("Build mobi!!!!")