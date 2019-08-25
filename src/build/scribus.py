from jinja2 import Template

import os
import .utils

def read_template(file_name):
    try:
        template_xml = open(file_name).read()
    except:
        raise Exception("The template file {} can't be opened or read".format(file_name))

    return Template( template_xml )


def build_pdf ( task_description, data_base, session_path, out_path) :
    """ Builds all the pdf configurations given the task_description
    """
    temp_folder = os.path.join(out_path, "temp")
    os.mkdir(temp_folder)

    temp_file_name = os.path.join(temp_folder, "temp_base_booklet.sla")
    base_booklet_file = open(temp_file_name, "w")

    if "template" not in task_description:
        print("there is no template defined for the PDF work!")
        return

    # read the configuration file for the template
    base_template_path = os.path.join(session_path, "templates", "scribus", task_description['template'])
    template_decription_file_name = os.path.join(base_template_path, "config.json")
    template_decription = read_json_file(template_decription_file_name)

    # read each layer, and aseemble them in a single file filling the gaps
    # A. base template
    cover_template_file_name = os.path.join(base_template_path, template_decription['cover']['filename'])
    cover_template = read_template(cover_template_file_name)


    # A. cover
    cover_template_file_name = os.path.join(base_template_path, template_decription['cover']['filename'])
    cover_template = read_template(cover_template_file_name)


    {
    "name": "monthly_booklet",
    "cover": {
        "filename": "cover.sla",
        "L": "Normal Left",
        "R": "Normal Right"
    },
    "main_text": {
        "filename": "base_booklet.sla",
        "L": "Normal Left",
        "R": "Normal Right"
    },
    "intro": {
        "filename": "intro.sla",
        "L": "Normal Left",
        "R": "Normal Right"
    },
    "prayers": {
        "filename": "prayers.sla",
        "L": "Normal Left",
        "R": "Normal Right"
    },
    "exam": {
        "filename": "exam.sla",
        "L": "Normal Left",
        "R": "Normal Right"
    }
}