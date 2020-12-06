
import os.path
from os import path
import pprint

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date, timedelta

from .namesSpecs import weekdays, monthNumber, getWeekDay, monthNames
from .parse import break_and_process_comments

SKIP_DAY_CODE = "white"

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
        self.gospel_long = ""
        self.onomastic = ""
        self.quote = ""
        self.comment = ""
        self.date = ""
        self.code = ""
        self.link = None
        self.comment_in_html = ""
        self.day_string = ""
        self.is_blank = False

    @classmethod
    def copy_contructor(cls, day_data, date_key):
        day = cls()
        day.day, day.month, day.year = split_date_key(date_key)
        day.version = day_data.version
        day.language = day_data.language
        day.week_day = day_data.week_day
        day.gospel = day_data.gospel
        day.gospel_long = day_data.gospel_long
        day.onomastic = day_data.onomastic
        day.quote = day_data.quote
        day.comment = day_data.comment
        day.date = day_data.date
        day.code = day_data.code
        day.link = day_data.link
        return day

    @classmethod
    def blank_day(cls, title = None):
        blank = cls()
        blank.title = title
        blank.is_blank = True
        return blank

    @property
    def blank(self):
        return self.is_blank        

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

    def getFullStringDay(self, language = None):
        language_ = language if language is not None else self.language
        wd = weekdays[language_][getWeekDay(self.day, self.month, self.year)]
        month_str = monthNames[language_][self.month]
        full_str_day = "%s %s %s" % (wd, self.get_string_day(), month_str)
        #print(language_, full_str_day)
        return full_str_day

    def getMonthString(self, language = None):
        language_ = language if language is not None else self.language
        return monthNames[language_][self.month]

    def getStringWeekDay(self, language = None):
        language_ = language if language is not None else self.language
        wd = weekdays[language_][getWeekDay(
            self.day, self.month, self.year)]
        return wd

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


class GoogleSpreadSheetMgr:
    gc = None
    current_credentials = ""
    language_databases = {}

    def __init__(self):
        pass

class DataBaseHandler:
    def __init__(self, spreadsheet_link, language = None, no_db_access = False):
        self.gs = spreadsheet_link
        self.days = {}
        self.language = language if language is not None else 'english'

        if no_db_access:
            return

        for sheet in self.gs:
            print("processing sheet {0} with {1} days.".format(sheet.title, sheet.col_count))
            sheet_day_values = sheet.get_all_values()

            min_size = sheet.row_count if sheet.row_count < len(sheet_day_values) else len(sheet_day_values)
            if min_size < sheet.row_count:
                print("There is something funny on the number of rows on the table {0}".format(sheet.title))

            keys_used_in_table = [sheet_day_values[i][0] for i in range(1, min_size)]

            for col in range(sheet.col_count-1):
                day_key = sheet_day_values[1][col+1]

                # check the format of this cell
                if day_key == "":
                    continue

                # read all the values of that particular day and match it against the keys
                day_info = { "language" : language }

                for value_idx in range(len(keys_used_in_table)):
                    if keys_used_in_table[value_idx] == "comment":
                        # preprocess the text
                        raw_comment = sheet_day_values[value_idx+1][col+1]
                        day_info["comment"] = break_and_process_comments(raw_comment)
                    else:
                        day_info[keys_used_in_table[value_idx]] = sheet_day_values[value_idx+1][col+1]

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

    def produce_days_from_list(self, list_of_days):
        days_collected = []
        
        for day_code in list_of_days:
            version = 0
        
            if day_code[1] == SKIP_DAY_CODE:
                title = None if len(day_code)<3 else day_code[2]
                new_day = DaySpec.blank_day( title = title )
                new_day.version = version
                days_collected.append( new_day )
                continue

            # run over all the entries for the day_code (date)
            for text_in_day in day_code[1:]:
                if text_in_day in self.days:
                    new_day = DaySpec.copy_contructor(self.days[text_in_day][0], day_code[0])
                    new_day.version = version
                    days_collected.append( new_day )                   
                else:
                    print("The text code {0} for day {1} is not the data base".format(text_in_day, day_code[0]))
                version += 1

        return days_collected


def load_db( credentials, scope):
    # Read data base for each language
    print("-- Building data base from google spreadsheets -- ")
    print("   Credentials used:", credentials)

    if not path.exists(credentials):
        print("The credentials file doesn't exists!")
        return

    if GoogleSpreadSheetMgr.current_credentials == credentials:
        return

    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
    GoogleSpreadSheetMgr.gc = gspread.authorize(credentials)

# will return a data base related to a language
def read_data_base(data_base_name, language, no_db_access = False):
    if language in GoogleSpreadSheetMgr.language_databases:
        return GoogleSpreadSheetMgr.language_databases[language]

    data_base_handle = GoogleSpreadSheetMgr.gc.open(data_base_name)

    if data_base_handle is None:
        return None

    print("Found a {0} data base.".format(language))

    GoogleSpreadSheetMgr.language_databases[language] = DataBaseHandler(data_base_handle, language, no_db_access)
    return GoogleSpreadSheetMgr.language_databases[language]

# Returns the list of days that a task will be processing
def read_list_of_days(list_name):
    tasks_path = list_name.split('/')
    if len(tasks_path) < 2:
        print("The path for the tasks database is not correct")
        return

    data_base_handle = GoogleSpreadSheetMgr.gc.open(tasks_path[0])

    if data_base_handle is None:
        return None

    ws = data_base_handle.worksheet(tasks_path[1])

    if data_base_handle is None:
        return None

    print("Reading list of days {1} from data base {0}.".format(tasks_path[0], tasks_path[1]))

    sheet_day_values = ws.get_all_values()
    days_to_proces = []
    for day_code_idx in range(len(sheet_day_values)):
        texts = []
        for text in range(len(sheet_day_values[day_code_idx])):
            if sheet_day_values[day_code_idx][text] != "":
                texts.append(sheet_day_values[day_code_idx][text])
        
        if len(texts) < 2:
            print("There is no texts on the day {0}", day_code_idx)
            continue

        days_to_proces.append(texts)

    return days_to_proces
