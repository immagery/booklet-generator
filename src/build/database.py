import calendar
from iPraybuild import basic_generator

from namesSpecs import *

from os import listdir
from os.path import isfile, join

def getAllFilesRecursive(directory, filter = ".txt"):
	files = []
	for f in listdir(directory):
		if not isfile(join(directory, f)):
			files = files + getAllFilesRecursive(join(directory, f))
		elif f.endswith(filter):
			files.append([directory,f])
	return files

# reads all the files on input folder and all subfolders and reads the contents
def addData(sourceBaseDirectory, year = "XXXX", DB_days = None):
    if not DB_days:
        DB_days = {}

    print "\n------------------------------------------------------------ "
    print "Processing imput files in: \"{0}\"".format(sourceBaseDirectory)

    onlyfiles = getAllFilesRecursive(sourceBaseDirectory)

    for fileName in onlyfiles:
        d = basic_generator.readContent(fileName[0]+'/',fileName[1])
        DB_days[fileName[1]] = d
        d.year = year
        print "{0} of {1} of {2} -> \"{3}\"".format(d.day_string, d.month, d.year, fileName[1])

    print len(DB_days.keys()), "days added to the DB!\n------------------------------------------------------------\n"

    return DB_days


def search(DB_days, monthDay, currentMonth, currentYear, seasonWeek, currentWeekday, season, language = "english", debug = False):
    #print "search"
    collectedDays = []
    for name, day in DB_days.items():
        if(debug):
            print "debug DB names:", monthDay, day.day_number, monthNames[language][currentMonth], day.month, currentYear, day.year
        if monthDay == day.day_number and monthNames[language][currentMonth] == day.month and currentYear == day.year:
            #print 'first', monthDay, monthNames[currentMonth]
            collectedDays.append(day)
        elif seasonWeek == day.seasonWeek and season == day.season and day.seasonWeekday == weekdays[language][currentWeekday]:
            collectedDays.append(day)
            #print 'second', seasonWeek, season, weekdays[currentWeekday]

    return collectedDays

def selectLeafletDays(definitions, DB_days, season, language = "english", debug = False):
    leafletDays = []

    dayIdx = 0
    monthDay = definitions['firstDay']
    currentMonth = monthNumber[language][definitions['firstMonth']]
    currentYear = definitions['firstYear']

    seasonWeek = definitions["Season"]['firstSeasonWeek']
    currentWeekday = getWeekDay(monthDay, currentMonth, currentYear)

    print "Starting Date: {0}, {1} of {2} of {3}".format(weekdays[language][currentWeekday], monthDay, monthNames[language][currentMonth], currentYear)

    totalDays = definitions['days']
    while dayIdx < totalDays:
    	#recorremos the list of days

    	while monthDay <= monthDays[currentMonth]:

            #procesar dia
            collectedDays = search(DB_days, monthDay, currentMonth, currentYear, seasonWeek, currentWeekday, season, language, debug)

            if len(collectedDays) != 1:
                print "[INFO] {0} {1} {2} -> {3} collectedDays".format(monthDay, currentMonth, currentYear, len(collectedDays))

            entry = daySpec( collectedDays, language = language )
            entry.day = monthDay
            entry.month = monthNames[language][currentMonth]
            entry.year = currentYear

    		#print 'found', len(entry.versions)
            leafletDays.append(entry)

            monthDay += 1
            dayIdx += max(len(entry.versions),1)
            #print 'dayIdx', dayIdx

            currentWeekday += 1

    		# next week
            if currentWeekday == 7:
                seasonWeek += 1

            if currentWeekday >= 8:
    			currentWeekday = 1

			#print 'click', entry.day,entry.month, entry.year, len(leafletDays), len(collectedDays), monthDay, currentMonth, seasonWeek, currentWeekday, season

			if dayIdx > totalDays:
				break

    	#next month
    	monthDay = 1
    	currentMonth += 1

    	#next year
    	if currentMonth >= 13:
    		currentYear += 1
    		currentMonth = 1

    return leafletDays
