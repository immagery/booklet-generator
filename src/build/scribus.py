from jinja2 import Template

import os

from .utils import read_json_file
from .gs_database import build_date_key


def read_template(file_name):
    try:
        template_xml = open(file_name, encoding="utf8").read()
    except Exception as e:
        raise Exception(
            "The template file {} can't be opened or read: {1}".format(file_name, str(e)))

    return Template(template_xml)


def build_pdf(pdf_config, data_base, task_path, session_path, out_path):
    """ Builds all the pdf configurations given the task_description
    """
    temp_folder = os.path.join(out_path, "temp")
    os.makedirs(temp_folder, exist_ok=True)

    temp_file_name = os.path.join(temp_folder, "temp_base_booklet.sla")
    base_booklet_file = open(temp_file_name, "w")

    if "template" not in pdf_config:
        print("there is no template defined for the PDF work!")
        return

    # read the configuration file for the template
    base_template_path = os.path.join(
        session_path, "templates", "scribus", pdf_config['template'])
    template_decription_file_name = os.path.join(
        base_template_path, "config.json")
    template_decription = read_json_file(template_decription_file_name)

    # read the configuration file for the leaflet
    task_decription_file_name = os.path.join(task_path, "config.json")
    task_description = read_json_file(task_decription_file_name)

    # compute the number of pages
    cover_pages = 2
    exam_pages = 1
    intro_pages = 3
    prayer_pages = 5
    pages_count = cover_pages + intro_pages + \
        task_description['text_count'] + exam_pages + prayer_pages

    # compute the pages that have to be added to round up for printing and so on
    additional_pages = 0
    if pages_count % 4 != 0:
        print(
            "Adding some white pages to round up the number to multiple of 4 for printing")
        additional_pages = pages_count % 4

    print("pages in the booklet before rounding up {0}".format(pages_count))
    pages_count = pages_count + additional_pages

    #   Building of the leaflet itself
    #   >> Read each layer, and asemble them in a single file filling the gaps
    leaflet_content = {}

    # A. cover
    cover_descr = template_decription['cover']
    cover_template_file_name = os.path.join(
        base_template_path, cover_descr['R'])
    # cover_template_right = read_template(cover_template_file_name)

    cover_template_file_name = os.path.join(
        base_template_path, cover_descr['L'])
    # cover_template_left = read_template(cover_template_file_name)

    last_cover_y_pos = (
        pages_count-1) * template_decription['page_height'] + cover_descr['right_y_pos']
    # cover_data = { "cover_image_path" : cover_descr['cover_image'],
    #               "last_cover_y_pos" : last_cover_y_pos }

    # cover_template_right.render(cover_data)
    leaflet_content['cover_begining'] = ""
    leaflet_content['cover_end'] = ""  # cover_template_left.render(cover_data)

    # B. Intro
    intro_descr = template_decription['intro']
    intro_template_file_name = os.path.join(
        base_template_path, intro_descr['filename'])
    intro_template = read_template(intro_template_file_name)

    leaflet_content['intro'] = ""

    tmp_descr = template_decription['main_content']
    tmp_descr['path'] = base_template_path
    tmp_descr['page_height'] = template_decription['page_height']
    task_description['first_page'] = cover_pages + intro_pages + 1

    first_date = build_date_key(
        task_description["first_day"],
        task_description["first_month"],
        task_description["first_year"])

    taks_days = data_base.produce_days(
        first_date, 
        task_description['text_count'])

    # C. text
    leaflet_content['main_content'] = generate_main_content(
        tmp_descr, task_description, taks_days)

    # D. exam
    leaflet_content['exam'] = ""

    # E. prayers
    leaflet_content['prayers'] = ""

    # copy base label
    for labels in template_decription['base_leaflet_labels']:
        leaflet_content[labels] = template_decription[labels]

    # overwrite those needed
    leaflet_content['page_count'] = pages_count

    # Put all the stuff into the base template
    base_template_file_name = os.path.join(
        base_template_path, template_decription['base_template'])
    base_template = read_template(base_template_file_name)

    baked_leaflet = base_template.render(**leaflet_content)
    base_booklet_file.write(baked_leaflet)
    base_booklet_file.close()


def generate_main_content(template, task_description, days):
    left_pages_file_name = os.path.join(
        template['path'], template['left_page']['filename'])
    left_pages_template = read_template(left_pages_file_name)

    right_pages_file_name = os.path.join(
        template['path'], template['right_page']['filename'])
    right_pages_template = read_template(right_pages_file_name)

    main_content = ""
    first_page = task_description['first_page']

    for page_id in range(len(days)):
        current_page = first_page + page_id
        base_y = template['page_height'] * (current_page / 2)

        # compute the new position for those pages
        page_data = {}
        for label in template['left_page']:
            if label == "filename":
                continue
            page_data[label] = base_y+template['left_page'][label]

        page_data['page_num'] = current_page

        # put the content
        page_data['gospel'] = build_gospel_items(
            days[page_id].gospel, template['gospel_item'])
        page_data['comment'] = build_comment_items(
            days[page_id].comment, template['comment_item'])
        page_data['onomastic'] = days[page_id].onomastic
        page_data['date'] = days[page_id].date
        page_data['quote'] = days[page_id].quote
        page_data['page_number_value'] = current_page

        if current_page % 2 == 0:
            # even -> left
            main_content = main_content + \
                left_pages_template.render(**page_data)
        else:
            # odd -> right
            main_content = main_content + \
                right_pages_template.render(**page_data)

    return main_content


def build_gospel_items(content, mini_template):
    return Template(mini_template).render(paragraph=content)


def build_comment_items(content, mini_template):
    composition = ""
    for paragraph in content:
        paragraph_text = ""
        for elem in paragraph:
            paragraph_text = paragraph_text + wrap_element(elem[0], (elem[1])

        composition = composition + \
            Template(mini_template).render(paragraph=paragraph_text)
    return composition

italic_template = "{{text}}"

def wrap_element(style, text):
    if style == 'normal':
        return text
    elif style == "italic":
        return 