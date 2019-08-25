import calendar

monthDays = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
monthNames = {"english": ['dummy', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
              "german":  ['dummy', 'Januar', 'Februar', 'Marz', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']}

weekdays = {"english": ['dummy', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            "german":  ['dummy', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']}


monthNumber = {"english": {},
               "german": {}}

for lan in monthNames.keys():
    for i in range(len(monthNames[lan])):
        monthNumber[lan][monthNames[lan][i]] = i

weekdayNumber = {"english": {},
                 "german": {}}

for lan in monthNames.keys():
    for i in range(len(weekdays[lan])):
        weekdayNumber[lan][weekdays[lan][i]] = i


def getWeekDay(day, month, year):
    cal = calendar.Calendar()
    for week in cal.monthdatescalendar(year, month):
        for dayIdx in range(len(week)):
            d = week[dayIdx]
            if d.day == day and d.month == month and d.year == year:
                return dayIdx+1

    return -1