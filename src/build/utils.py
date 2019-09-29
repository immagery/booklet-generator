import zipfile
import re
import copy
import os
import shutil

from jinja2 import Template
import json

def read_template(file_name):
    try:
        template_xml = open(file_name, encoding="utf-8").read()
    except Exception as e:
        raise Exception(
            "The template file {} can't be opened or read: {1}".format(file_name, str(e)))

    return Template(template_xml)

def zip_tree(tree, destination):
    #http://stackoverflow.com/a/17080988/113036
    relroot = os.path.abspath(os.path.join(tree, os.pardir))
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(tree):
            # add directory (needed for empty dirs)
            #zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, tree), file)
                    zip.write(filename, arcname)

def copyDirectory(src, dest):
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        newDest = os.path.join(dest, file_name)
        if (os.path.isfile(full_file_name)):
            shutil.copy(full_file_name, dest)
        else:
            os.mkdir(newDest)
            copyDirectory(full_file_name, newDest)

def read_json_file(file_name):
    """Returns a dictionary as representation of the json file file_name.

    :param file_name: path to the json file to read
    :type file_name: str

    """
    try:
        file_name_text = open(file_name, "r").read()
    except:
        raise Exception("The configuration file {} could not be opened.".format(file_name_text))

    return json.loads( file_name_text )