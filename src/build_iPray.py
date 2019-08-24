#import iPray_full_2019

#baseTextsDirectory = "/Users/jorgeboronat/Documents/iPray_book/3plus2/3plus2_text/2019/"
#baseProcessDirectory = "/Users/jorgeboronat/Documents/iPray_book/iPray/"

#!/usr/bin/python

import json
import sys
import os

from build.scribus import read_template

def read_json_file(file_name):
    try:
        file_name_text = open(file_name, "r").read()
    except:
        raise Exception("The configuration file {} could not be opened.".format(file_name_text))

    return json.loads( booklet_base_config )

if len(sys.argv) <= 1:
    print("Help...")
    sys.exit()

session_path = sys.argv[1]
booklet_base_config_file = os.path.join(session_path, "config.json")
print("Reading configuration from path:", booklet_base_config_file)

# Read the configuration of this booklet
config = read_json_file( booklet_base_config_file )

languages_in_session = config['languages']

for booklet_name in config['leaflets'].keys():
    print("Processing booklet: ", booklet_name)
    leaflet_base_folder =  os.path.join(session_path, config['leaflets'][booklet_name], "config.json")

    booklet_template = read_template(config['booklet_template'))

    

template = read_template(file_name)

data = {
"pages" : "<PAGE PAGEXPOS=\"100\" PAGEYPOS=\"479.53\"/>",
"page_objects" : "<PAGEOBJECT OwnPage=\"0\" PTYPE=\"4\" XPOS=\"580.25\" YPOS=\"38\" />"}

result = template.render( **data )

print(result)

