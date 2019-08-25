import pprint
from datetime import date, timedelta

from .namesSpecs import monthNumber, weekdays, getWeekDay
from .parse import break_and_process_comments


def split_date_key(date_key):
    if '/' in date_key:
        elements = date_key.split('/')
        if len(elements) == 3:
            return int(elements[0]), int(elements[1]), int(elements[2])
    return 1, 1, 2019


def build_date_key(day, month, year):
    day_str = str(day) if day >= 10 else "0"+str(day)
    month_str = str(month) if month >= 10 else "0"+str(month)
    return "{0}/{1}/{2}".format(day_str, month_str, year)


def get_week_day(day, month, year):
    cal = calendar.Calendar()
    for week in cal.monthdatescalendar(year, month):
        for dayIdx in range(len(week)):
            d = week[dayIdx]
            if d.day == day and d.month == month and d.year == year:
                return dayIdx+1
    return -1


class DaySpec(object):
    def __init__(self):
        self.day = 1
        self.month = 1
        self.year = 2019
        self.version = 0
        self.language = 'english'
        self.week_day = 1
        self.gospel = ""
        self.quote = ""
        self.comment = ""
        self.date = ""
        self.code = ""
        self.link = None

    @classmethod
    def from_day_raw_data(cls, day_data, date_key, version=0):
        ''' Fill this class with the values in the dictionary if there is any matching
        '''
        day = cls()
        for attr in day_data.keys():
            if attr in day.__dict__:
                day.__dict__[attr] = day_data[attr]
        day.version = version
        day.day, day.month, day.year = split_date_key(date_key)
        return day

    def getFullStringDay(self):
        print(monthNumber[self.language].keys())
        wd = weekdays[self.language][getWeekDay(
            self.day, monthNumber[self.language][self.month], self.year)]
        return "%s %s %s" % (wd, self.get_string_day(), self.month)

    def get_string_day(self):
        if self.day % 10 == 1 and self.day != 11:
            return str(self.day)+'st'
        if self.day % 10 == 2 and self.day != 12:
            return str(self.day)+'nd'
        if self.day % 10 == 3 and self.day != 13:
            return str(self.day)+'rd'

        return str(self.day)+'th'

    def printData(self):
        return self.get_string_day(), self.month, self.year, '('+str(len(self.version))+')'

    def getUniqueLink(self):
        return str(self.day)+"_"+str(self.month)+"_"+str(self.year)+"_"+str(self.version)

    def __repr__(self):
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(self.__dict__)


class DataBaseHandler:
    def __init__(self, spreadsheet_link):
        self.gs = spreadsheet_link
        self.days = {}

        for sheet in self.gs:
            print("processing sheet {0} with {1} days.".format(
                sheet.title, sheet.col_count))
            sheet_day_values = sheet.get_all_values()

            keys_used_in_table = [sheet_day_values[i][0]
                                  for i in range(sheet.col_count+1)]
            keys_count = len(keys_used_in_table)
            for col in range(1, sheet.col_count):
                day_key = sheet_day_values[0][col]

                # check the format of this cell
                if day_key == "":
                    continue

                # read all the values of that particular day and match it against the keys
                day_info = {}
                for value_idx in range(0, keys_count):
                    if keys_used_in_table[value_idx] == "comment":
                        # preprocess the text
                        raw_comment = sheet_day_values[value_idx][col]
                        day_info["comment"] = break_and_process_comments(raw_comment)
                    else:
                        day_info[keys_used_in_table[value_idx]
                                 ] = sheet_day_values[value_idx][col]

                # inject the new day
                self._add_or_append(day_key, day_info)

    def _add_or_append(self, key, day):
        ''' Adding a day under the same key (day, month, year) and increase the version count if
            there is already a day with that key '''
        if key not in self.days:
            self.days[key] = [DaySpec.from_day_raw_data(day, key)]
        else:
            new_day = DaySpec.from_day_raw_data(day, key, len(self.days[key]))
            self.days[key].append(new_day)

    def produce_days(self, first_date, num_of_days):
        days_collected = []
        day, month, year = split_date_key(first_date)

        start = date(year, month, day)
        counter = 0 # it's a safety net, if it doesn't find the days is looking for.
        time_delta = timedelta(days=1)
        while(counter <= num_of_days and len(days_collected) < num_of_days):
            day_key = build_date_key(start.day, start.month, start.year)
            
            # if the date is on the data base, we take any content for that day
            if day_key in self.days:
                for day_item in self.days[day_key]:
                    days_collected.append(day_item)

            start = start + time_delta
            counter = counter+1

        return days_collected


def read_data_base(spreadsheet):
    data_mgr = DataBaseHandler(spreadsheet)
    return data_mgr
