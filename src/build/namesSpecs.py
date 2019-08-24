import calendar

monthDays = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthNames = { "english" : ['dummy','January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
			   "german" :  ['dummy','Januar', 'Februar', 'Marz', 'April'  , 'Mai'  ,'Juni' ,'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'] }

weekdays   = { "english" : ['dummy','Monday' ,'Tuesday'  ,'Wednesday','Thursday','Friday','Saturday','Sunday'],
 			   "german" :  ['dummy','Montag' ,'Dienstag'  ,'Mittwoch','Donnerstag','Freitag','Samstag','Sonntag'] }


monthNumber = { "english" : {},
				"german" : {} }

for lan in monthNames.keys():
	for i in range(len(monthNames[lan])):
		monthNumber[lan][monthNames[lan][i]] = i

weekdayNumber = { "english" : {},
				  "german" : {} }

for lan in monthNames.keys():
	for i in range(len(weekdays[lan])):
		weekdayNumber[lan][weekdays[lan][i]] = i

def getWeekDay(day, month, year):
	cal = calendar.Calendar()
	for week in cal.monthdatescalendar(year, month):
		for dayIdx in range(len(week)):
			d = week[dayIdx]
			if d.day == day and d.month == month and d.year==year:
				return dayIdx+1

	return -1

class dayObj ( object ):
	def __init__( self ):
		self.init = False
		self.day_number = 0
		self.day_string = 'not set'
		self.month = 'not set'
		self.year = 'XXXX'
		self.version = 0
		self.gospel = ''
		self.citation = ''
		self.comment = ''
		self.area = 'All'
		self.saint = ''

		self.link= None
		self.season = None
		self.seasonWeek = None
		self.seasonWeekday = None
		self.isFeastDay = False

		self.originalFile = ''


	def getDataForPrint( self ):
		return 'Day: %s %s %s %s %s %s %s %s' %(self.day_string, self.month, str(self.year), str(self.version), self.area, self.season, self.seasonWeek, self.seasonWeekday)

	def printAllData( self ):
		print 'day_number:', self.day_number
		print 'day_string:', self.day_string
		print 'month:', self.month
		print 'year:', self.year
		print 'version:', self.version
		print 'gospel:', self.gospel
		print 'citation:', self.citation
		print 'comment:', self.comment
		print 'area:', self.area
		print 'saint:', self.saint

	def getUniqueLink( self ):
		return str(self.day_string)+"_"+str(self.month)+"_"+str(self.year)

class daySpec( object ):
	def __init__(self, versions = None, language = "english"):
		self.day = 1
		self.month = monthNames['english'][0]
		self.year = 2018
		self.versions = versions
		self.language = language


	def getFullStringDay(self):
		print monthNumber[self.language].keys()
		wd = weekdays[self.language][getWeekDay(self.day, monthNumber[self.language][self.month] ,self.year)]
		return "%s %s %s" % (wd, self.getStringDay(), self.month)

	def getStringDay(self):
		if self.day%10 == 1 and self.day != 11:
			return str(self.day)+'st'
		if self.day%10 == 2 and self.day != 12:
			return str(self.day)+'nd'
		if self.day%10 == 3 and self.day != 13:
			return str(self.day)+'rd'

		return str(self.day)+'th'

	def printData(self):
		return self.getStringDay(), self.month, self.year , '('+str(len(self.versions))+')'
