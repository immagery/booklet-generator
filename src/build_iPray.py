import json
import sys
import os

from build.utils import read_json_file
from build.gs_database import load_db, read_data_base
from build import build_functions

# merges the two dictionaries, with child values having preference
def merge_config_files( parent_config, child_config ):

    # base case on the recursive function
    # in the case of not being a dictionary, it will copy
    # the child value that is. Including vectors
    if not isinstance(child_config, dict):
        return child_config.deepcopy()

    # we only merge it if it's a dictionary
    new_config = parent_config.deepcopy()
    for key, value in child_config:
        if key in new_config:
            new_config[key] = merge_config_files(new_config[key], child_config[key])
        else:
            new_config[key] = value.deepcopy()
    
    return new_config

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

# merge the child config (base_config) into the parent (session_config)
session_config = merge_config_files(session_config, base_config)

# set up the global database
credentials_filename = os.path.join(session_path, "credentials", session_config['credentials'])
load_db( credentials = credentials_filename, scope = session_config['scope'])

# Read days data base for each language
data_base = {}
for language, data_base_name in session_config['spreadsheet'].items():
    db = read_data_base(data_base_name, language)
    
    if db is None:
        continue

    data_base[language] = db 

# Build the different mediums based on the tasks config file
for task_name, task_folder in session_config['tasks'].items():
    print("Processing tasks {0}".format(task_name))

    # read the configuration task for the leaflet
    task_path = os.path.join(session_path, base_config_path, task_folder)
    task_decription_file_name = os.path.join(task_path, "config.json")
    task_description = read_json_file(task_decription_file_name)

    # merge the child config (session_config) into the parent (task_description)
    task_config = merge_config_files(session_config, task_description)

    for language in task_config['languages']:

        if language not in task_config['spreadsheet']:
            print(
                "Skiping language ({0}), as it's not defined in the database.".format(language))
            continue

        for medium in task_config['mediums']:
            if medium not in build_functions:
                print(
                    "Skiping medium ({0}), as it doesn't exist.".format(medium))
                continue
            
            # if it's not enable we skip that medium
            if 'enable' in task_config['mediums'][medium].keys():
                if not task_config['mediums'][medium]['enable']:
                    print("Skipping medium {0} in {1}".format(medium, language))
                    continue

            print("Building {0} in {1}".format(medium, language))

            # figure out the paths for this task, input and output
            out_path = os.path.join(
                session_path, session_config["export_path"], language, base_config_path, task_folder, medium)

            build_functions[medium](task_config, data_base[language], task_path, session_path, out_path)
