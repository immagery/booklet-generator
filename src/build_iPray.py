import json
import sys
import os

from build.utils import read_json_file
from build.gs_database import read_data_base
from build import build_functions

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# check parameters
if len(sys.argv) <= 2:
    print("The number parameters don't seems to be correct, the right syntax is:")
    print("build_iPray session-path task")
    sys.exit()

# Initializing session, this will define all the paths used
session_path = sys.argv[1]
session_file = os.path.join(session_path, "config.json")
session_config = read_json_file(session_file)

print("Loading session: ", session_config['description'])
print("Created on: ", session_config['creation'])

# Read the configuration of tasks to do
base_config_path = sys.argv[2]
base_config_file = os.path.join(session_path, base_config_path, "config.json")
print("Reading configuration from path:", base_config_file)
base_config = read_json_file(base_config_file)

# Read data base for each language
credentials_filename = os.path.join(
    session_path, "credentials", session_config['credentials'])
print("credentials used", credentials_filename)
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    credentials_filename, session_config['scope'])
gc = gspread.authorize(credentials)

data_base = {}
for language, data_base_name in base_config['spreadsheet'].items():
    data_base_handle = gc.open(data_base_name)

    if data_base_handle is None:
        continue

    print("Found a {0} data base.".format(language))
    data_base[language] = read_data_base(data_base_handle, language)

# Build the different mediums based on the tasks config file
for task_name, task_folder in base_config['tasks'].items():
    print("Processing tasks {0}".format(task_name))

    # read the configuration file for the leaflet
    task_path = os.path.join(session_path, base_config_path, task_folder)
    task_decription_file_name = os.path.join(task_path, "config.json")
    task_description = read_json_file(task_decription_file_name)

    for language in base_config['languages']:

        if language not in base_config['spreadsheet']:
            print(
                "Skiping language ({0}), as it's not defined in the database.".format(language))
            continue

        for medium in task_description['mediums']:
            if medium not in build_functions:
                print(
                    "Skiping medium ({0}), as it doesn't exist.".format(medium))
                continue

            print("Building {0} in {1}".format(medium, language))

            # figure out the paths for this task, input and output
            out_path = os.path.join(
                session_path, session_config["export_path"], language, base_config_path, task_folder, medium)

            build_functions[medium](task_description, data_base[language], task_path, session_path, out_path)
