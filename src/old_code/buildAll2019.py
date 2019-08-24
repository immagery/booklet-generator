#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import os
#os.environ['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

#import iPraybuild
#import iPray2019

import sys
import os

sys.path.insert(0, os.path.abspath('..'))

# collect all the things to process based on a folder, it could be changed by a UI selection thing.

language = "english"
possible_languages = ["english", "german"]

if len(sys.argv) > 1:
    folder_to_proces = sys.argv[1]

if len(sys.argv) > 2:
    language_temp = sys.argv[2]
    if language_temp and language_temp not in possible_languages:
        raise Exception ( str(language_temp) + " is not a valid language.")        
    language = language_temp
    

if not os.path.isdir(os.path.abspath('.') + "\\" + sys.argv[1]):
    if not os.path.exists(os.path.abspath('.') + "\\" + sys.argv[1]):
        raise Exception ("The folder or file to process doesn't exist: "+os.path.abspath('.') + "\\" + sys.argv[1])

# call the function to process each of them, handle exceptions so we can show them in the UI and the command line.