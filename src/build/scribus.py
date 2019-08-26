from jinja2 import Template

import os
from shutil import copyfile

from .utils import read_json_file
from .gs_database import build_date_key


def read_template(file_name):
    try:
        template_xml = open(file_name, encoding="utf-8").read()
    except Exception as e:
        raise Exception(
            "The template file {} can't be opened or read: {1}".format(file_name, str(e)))

    return Template(template_xml)


def build_pdf(task_description, data_base, task_path, session_path, out_path):
    """ Builds all the pdf configurations given the task_description
    """
    temp_folder = os.path.join(out_path, "temp")
    os.makedirs(temp_folder, exist_ok=True)

    temp_file_name = os.path.join(temp_folder, "temp_base_booklet.sla")
    base_booklet_file = open(temp_file_name, "w", encoding="utf-8")

    pdf_config = task_description['mediums']['pdf']

    if "template" not in pdf_config:
        print("there is no template defined for the PDF work!")
        return

    # read the configuration file for the template
    base_template_path = os.path.join(
        session_path, "templates", "scribus", pdf_config['template'])
    template_decription_file_name = os.path.join(
        base_template_path, "config.json")
    template_decription = read_json_file(template_decription_file_name)

    # compute the pages that have to be added to round up for printing and so on
    #additional_pages = 0
    # if pages_count % 4 != 0:
    #    print(
    #        "Adding some white pages to round up the number to multiple of 4 for printing")
    #    additional_pages = pages_count % 4

    #print("pages in the booklet before rounding up {0}".format(pages_count))
    #pages_count = pages_count + additional_pages

    #   Building of the leaflet itself
    #   >> Read each layer, and asemble them in a single file filling the gaps
    current_page = 0
    leaflet_content = {}

    # A. cover
    cover_descr = template_decription['cover']
    cover_template_file_name = os.path.join(
        base_template_path, cover_descr['R'])
    cover_template_right = read_template(cover_template_file_name)

    # grab and copy the image into the temp directory,
    # to have it relative to the scribus document.
    if data_base.language in pdf_config['cover_image']:
        image_file_name = pdf_config['cover_image'][data_base.language]
    else:
        image_file_name = pdf_config['cover_image']['english']
    image_file_path = os.path.join(task_path, image_file_name)
    try:
        copyfile(image_file_path, os.path.join(
            temp_folder, "pdf_cover_image.jpg"))
    except IOError as e:
        print(
            "Unable to copy the cover image to generate the pdf. [{0}]".format(e))

    # front cover
    leaflet_content['cover_begining'] = cover_template_right.render()
    current_page = 1

    white_template_file_name = os.path.join(base_template_path, template_decription['white_page'])
    white_template = read_template(white_template_file_name)
    white_page_insert = white_template.render(page_num=current_page)
    leaflet_content['cover_begining'] = leaflet_content['cover_begining'] + white_page_insert
    current_page = current_page + 1

    # B. Intro
    intro_descr = template_decription['intro']
    intro_template_file_name = os.path.join(
        base_template_path, intro_descr['filename'])
    intro_template = read_template(intro_template_file_name)

    leaflet_content['intro'] = intro_template.render(page_0=current_page)
    intro_pages = 3
    current_page = current_page + intro_pages

    # white page insert
    white_page_insert = white_template.render(page_num=current_page)
    current_page = current_page + 1

    # C. main text
    tmp_descr = template_decription['main_content']
    tmp_descr['path'] = base_template_path
    tmp_descr['page_height'] = template_decription['page_height']
    tmp_descr['character_style_templates'] = template_decription['character_style_templates']
    task_description['first_page'] = current_page

    first_date = build_date_key(
        task_description["first_day"],
        task_description["first_month"],
        task_description["first_year"])

    taks_days = data_base.produce_days(
        first_date,
        task_description['text_count'])

    leaflet_content['main_content'] = white_page_insert + generate_main_content(
        tmp_descr, task_description, taks_days)

    comments_pages = len(taks_days)
    current_page = current_page + comments_pages

    # D. exam
    leaflet_content['exam'] = ""
    exam_pages = 0
    current_page = current_page + exam_pages

    # E. prayers
    leaflet_content['prayers'] = ""
    prayers_pages = 0
    current_page = current_page + prayers_pages

    white_page_insert = white_template.render(page_num=current_page)
    current_page = current_page + 1

    # F. final cover
    base_y_pos = ((current_page+1) // 2) * \
        (template_decription['page_height']+40)
    cover_data = {"page_num": current_page,
                  "page_y_pos": base_y_pos,
                  "image_y_pos": base_y_pos + cover_descr['image_y_pos']}

    cover_template_file_name = os.path.join(
        base_template_path, cover_descr['L'])
    cover_template_left = read_template(cover_template_file_name)
    leaflet_content['cover_end'] = cover_template_left.render(**cover_data)

    leaflet_content['cover_end'] =  white_page_insert + leaflet_content['cover_end']
    current_page = current_page + 1

    # copy base label
    for labels in template_decription['base_leaflet_labels']:
        leaflet_content[labels] = template_decription[labels]

    # overwrite those needed
    leaflet_content['page_count'] = current_page

    # Put all the stuff into the base template
    base_template_file_name = os.path.join(
        base_template_path, template_decription['base_template'])
    base_template = read_template(base_template_file_name)

    print("output file: ", temp_file_name)
    baked_leaflet = base_template.render(**leaflet_content)
    base_booklet_file.write(baked_leaflet)
    base_booklet_file.close()


def generate_main_content(template, task_description, days):
    left_pages_file_name = os.path.join(
        template['path'], template['left_page'])
    left_pages_template = read_template(left_pages_file_name)

    right_pages_file_name = os.path.join(
        template['path'], template['right_page'])
    right_pages_template = read_template(right_pages_file_name)

    main_content = ""
    first_page = task_description['first_page']

    for page_id in range(len(days)):
        current_page = first_page + page_id
        base_y = (template['page_height']+40.0) * ((current_page+1) // 2)

        print("Building page {0}, with height {1}".format(
            current_page, base_y))

        # compute the new position for all the elements of those pages
        page_data = {}
        for label in template['y_displacement']:
            page_data[label] = base_y+template['y_displacement'][label]

        page_data['page_num'] = current_page

        # put the content
        page_data['gospel'] = build_gospel_items(
            days[page_id].gospel, template['gospel_item'])
        page_data['comment'] = build_comment_items(
            days[page_id].comment, template['comment_item'], template['character_style_templates'])
        page_data['onomastic'] = days[page_id].onomastic
        page_data['date'] = days[page_id].getFullStringDay()
        page_data['quote'] = days[page_id].quote
        page_data['page_number_value'] = str(current_page)

        if current_page % 2 == 1:
            # even -> left
            main_content = main_content + \
                left_pages_template.render(**page_data)
        else:
            # odd -> right
            main_content = main_content + \
                right_pages_template.render(**page_data)

    return main_content


def build_gospel_items(content, mini_template):
    return Template(mini_template).render(paragraph=content.replace("\"", "&quot;"))


def build_comment_items(content, paragraph_template, block_templates):
    composition = ""
    for paragraph in content:
        paragraph_text = ""
        for elem in paragraph:
            elem_wrap = Template(block_templates[elem[0]]).render(
                text=elem[1].replace("\"", "&quot;"))
            paragraph_text = paragraph_text + elem_wrap

        composition = composition + \
            Template(paragraph_template).render(paragraph=paragraph_text)

    return composition
