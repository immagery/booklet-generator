from os import listdir
from os.path import isfile, join
import parse as p
import os
import shutil

import utils
import basic_generator as gen

weekDayNames = [ "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" ]

def getCommentStylized(comment):
	content = ""
	for p in comment:
		content = content + "<p>"
		for b in p:
			content = content + b[1]
		content = content + "</p>\n"
	return content


def generateContent(saint, day, citation, gospel, comment, number, weekDays, monthDays):
	# header
	content =""
	if number > 0:
		content = "\t<hr/>"

	'''
	content = content + "\t<div><a href=\"tableOfContents.xhtml\">Go back to the index</a></div>"
	content = content + "\t<div id=\"contentDay_"+str(number)+"\">\n"
	content = content + "\t<div class=\"dayTittle\" >"+day+"</div>\n"
	if saint != "":
		content = content  + "\t<div class=\"saintTittle\"> - "+saint+"</div>\n"		
	'''

	dayOfTheWeek = weekDays[number]
	dayOfTheMonth = monthDays[number]

	content = content + "\t<div id=\"contentDay_"+str(number)+"\">\n"
	content = content + "\t<div class=\"space\" ></div>"
	content = content + "\t<div class=\"superday\">"+dayOfTheMonth
	content = content + "<a class=\"back_cal\" href=\"tableOfContents.xhtml\"> [calendar]</a></div>"
	#content = content + "\t<div><div class=\"dayTittle\" >"+dayOfTheWeek+"</div>"
	if saint != "":
		content = content  + "\t<div class=\"saintTittle\">"+saint+"</div>\n"		

	content = content  + "\t<div class=\"quote\"> "+citation+"</div>\n"

	# gospel
	content = content  + "\t<div class=\"gospel\">" + gospel + "</div>\n"

	# comment
	subcontent = getCommentStylized(comment)
	content = content + "\t<div>" + subcontent + "</div>\n</div>\n"
	return content


def fillXhtmlContents( comments, gospel, 
				  	   citation, days, saints, 
				       definitions, weekDays, dayComposition):
	pageId = 0

	# read template
	#extFile = open(definitions["finalContentFile"], 'r')
	#fileContent = str(extFile.read())
	#extFile.close()

	# put new content
	#tittleTag = "iPrayTittle"
	#contentTag = "iPrayContent"

	#contentPos = fileContent.find(contentTag)
	#tittlePos = fileContent.find(tittleTag)
	
	#newFileContent = fileContent[:tittlePos]
	#newFileContent = newFileContent + definitions["bookletName"]
	#newFileContent = newFileContent + fileContent[tittlePos + len(tittleTag):contentPos]

	intro = '''
	<?xml version="1.0" encoding="utf-8"?>
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
	  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

	<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
	  <title>Sometittle</title>
	  <link rel="stylesheet" href="stylesheet.css" type="text/css" />
	</head>
	<body>

	'''

	end = '''
	
	</body>
	</html>
	'''


	for i in range(len(comments)) :
		if i > definitions["TEXTS_NUM"]:
			continue

		# create html content
		dailyContent = generateContent(saints[pageId], days[pageId], citation[pageId], gospel[pageId], comments[pageId], pageId, weekDays, dayComposition)

		dailyContent = intro+dailyContent+end

		#newFileContent = newFileContent + dailyContent
		fileName = definitions["appAndroidResult"]+definitions["monthFigures"]+"-"+str(i+1)+".html"
		print fileName
		extFile = open(fileName, 'w')
		extFile.write(dailyContent)
		extFile.close()		
		pageId = pageId+1

	#newFileContent = newFileContent + fileContent[contentPos+len(contentTag):]

	# save file


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

def createIndexAndStructure(definitions, weekDays, dayComposition):

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

	numberIdx = 0
	counter = 0
	tableOfContexts = ""
	for month in definitions["months"]:
		monthDef = definitions["monthLimits"][month]
		year = int(monthDef["year"])
		firstDay = int(monthDef["firstDay"])
		duration = int(monthDef["long"])
		weekDay = int(monthDef["firstWeekDay"])

		monthTable = "<div>\n"
		monthTable = monthTable + "<div id=\"evcal_head\" class=\"calendar_header \">\n"
		monthTable = monthTable + "<p id=\"evcal_cur\">"+ month.upper() + " " + str(year) + "</p>\n"
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

  		number = firstDay
  		weekDayIdx = 0
  		for i in range(0,weekDay):			
	  		# empty days
	  		monthTable = monthTable + "<p class=\"evo_fc_day on_focus\" >-</p>\n"
	  		weekDayIdx = (weekDayIdx + 1)%7

	  	for i in range(duration-7):
  			# non empty days
  			#monthTable = monthTable + "<p class=\"evo_fc_day\" ><a href=content#contentDay_"+str(number)+">"+str(number)+"</a></p>\n"
  			monthTable = monthTable + "<p class=\"evo_fc_day\" ><a href=\"content.xhtml#contentDay_"+str(numberIdx)+"\">"+str(number)+"</a></p>\n"
  			dayComposition.append(composeDay(number, month))
  			number = number + 1
  			numberIdx = numberIdx + 1
			weekDays.append(weekDayDef(weekDayIdx))
  			weekDayIdx = (weekDayIdx + 1)%7

  		for i in range(min(duration-1,6)):
  			# end of column
  			monthTable = monthTable + "<p class=\"evo_fc_day bb\" ><a href=\"content.xhtml#contentDay_"+str(numberIdx)+"\">"+str(number)+"</a></p>\n"
  			dayComposition.append(composeDay(number, month))
  			number = number + 1
  			numberIdx = numberIdx + 1
  			weekDays.append(weekDayDef(weekDayIdx))
  			weekDayIdx = (weekDayIdx + 1)%7

  		# end
  		monthTable = monthTable + "<p class=\"evo_fc_day br bb\" ><a href=\"content.xhtml#contentDay_"+str(numberIdx)+"\">"+str(number)+"</a></p>\n"
  		monthTable = monthTable + "<div class=\"clear\"></div>\n"
  		monthTable = monthTable + "</div>\n"
  		monthTable = monthTable + "</div>\n"
  		monthTable = monthTable + "</div>\n"
  		monthTable = monthTable + "<div class=\"clear\"></div>\n"
  		monthTable = monthTable + "</div>\n"
  		monthTable = monthTable + "<div class=\"clear\"></div>\n"
  		monthTable = monthTable + "</div>\n"
  		weekDays.append(weekDayDef(weekDayIdx))
  		dayComposition.append(composeDay(number, month))

  		tableOfContexts = tableOfContexts + monthTable

  	# link to other contents
  	linksMoreContents = "<div><h3><a href=\"commonPrayers.xhtml\">Common Prayers</a></h3></div>"

	newFileContent = block1+tableOfContexts+linksMoreContents+block3

	contentFile = open(definitions["tableOfContentFile"], 'w')
	contentFile.write(newFileContent)
	contentFile.close()
	
def processAndroidLeaflet( definitions ):

	if os.path.exists(definitions["appAndroidResult"]):
		shutil.rmtree(definitions["appAndroidResult"])
	
	os.mkdir(definitions["appAndroidResult"])

	#utils.copyDirectory(definitions["ePubTemplate"],definitions["result"])

	weekDays = []
	dayComposition = []
	
	createIndexAndStructure(definitions, weekDays, dayComposition)

	#read the content for filling
	comments = {}
	gospel = {}
	citation = {}
	days = {}
	saints = {}
	textContents = gen.getTextContentToLoad(definitions)
	gen.readContents(textContents, comments, gospel, citation, days, saints, definitions)

	#Fill the the idml with the contents
	#pageId = fillXhtmlContents( comments, gospel, 
	#  						   citation, days, saints, 
	#  						   definitions, weekDays, dayComposition)

	pageId = fillXhtmlContents( comments, gospel, 
	  						   citation, days, saints, 
	  						   definitions, weekDays, dayComposition)

	print "Builded " + str(pageId) +" days!"

	# copy the right cover
	#shutil.copyfile(definitions["coverFile"],definitions["finalCoverFile"])
	#shutil.copyfile(definitions["logoFile"],definitions["finalLogoFile"])

	#compress the set as an ePub File
	#utils.zip_tree(definitions["result"], definitions["result"][:len(definitions["result"])-1]+".epub")
	#shutil.rmtree(definitions["result"])

	print "congratulations: app files produced!!!"


