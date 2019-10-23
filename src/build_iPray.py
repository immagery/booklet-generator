import json
import sys
import os

from build.utils import read_json_file
from build.gs_database import load_db, read_data_base
from build import build_functions

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

# set up the global database
credentials_filename = os.path.join(session_path, "credentials", session_config['credentials'])
load_db( credentials = credentials_filename, scope = session_config['scope'])

# Read days data base for each language
data_base = {}
for language, data_base_name in base_config['spreadsheet'].items():
    db = read_data_base(data_base_name, language)
    
    if db is None:
        continue

    data_base[language] = db 

# Build the different mediums based on the tasks config file
for task_name, task_folder in base_config['tasks'].items():
    print("Processing tasks {0}".format(task_name))

    # read the configuration task for the leaflet
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
            
            # if it's not enable we skip that medium
            if 'enable' in task_description['mediums'][medium].keys():
                if not task_description['mediums'][medium]['enable']:
                    print("Skipping medium {0} in {1}".format(medium, language))
                    continue

            print("Building {0} in {1}".format(medium, language))

            # figure out the paths for this task, input and output
            out_path = os.path.join(
                session_path, session_config["export_path"], language, base_config_path, task_folder, medium)

            build_functions[medium](task_description, data_base[language], task_path, session_path, out_path)
