from jinja2 import Template

import os
from shutil import copyfile

from .utils import read_json_file
from .gs_database import build_date_key

import xml.etree.ElementTree as ET


def read_template(file_name):
    try:
        template_xml = open(file_name, encoding="utf-8").read()
    except Exception as e:
        raise Exception(
            "The template file {} can't be opened or read: {1}".format(file_name, str(e)))

    return Template(template_xml)

basic_xml_header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

class TemplatePage:

    def __init__(self, page_header, ref_pos_x=100.00062992126, ref_pos_y=20.0012598425197):
        # localise and add an object
        self.number = int(page_header.attrib['NUM'])

        # Current position of the page
        self.pos_x = 0.0
        self.pos_y = 0.0

        # where the origin of the page is related to the frame
        self.ref_pos_x = ref_pos_x
        self.ref_pos_y = ref_pos_y

        # to compute all the objects in reference to the current page
        self.offset_x = float(page_header.attrib['PAGEXPOS'])-self.ref_pos_x
        self.offset_y = float(page_header.attrib['PAGEYPOS'])-self.ref_pos_y
        
        print("PAGE:({0})".format(self.number), 
                       float(page_header.attrib['PAGEXPOS']), 
                       float(page_header.attrib['PAGEYPOS']), 
                       self.ref_pos_x, 
                       self.ref_pos_y, 
                       self.offset_x, 
                       self.offset_y)

        # reference to the original xml description
        self.header = page_header

        # list of objects part of this page
        self.page_objects = []

    def add_object(self, page_obj):
        # localise and add an object to the list
        page_obj.pos_offset_x = page_obj.pos_offset_x - self.offset_x
        page_obj.pos_offset_y = page_obj.pos_offset_y - self.offset_y

        self.page_objects.append(page_obj)
        page_obj.page_owner = self

    def set_page_position( self, base_x, base_y, page_number):
        # update parameters of this page, so we can propagate it to the object
        self.number = page_number
        self.pos_x = self.ref_pos_x + base_x
        self.pos_y = self.ref_pos_y + base_y

        # progate to the all the objects
        for obj in self.page_objects:
            obj.set_object_position(base_x, base_y)

    def render( self ):
        # update xml header
        self.header.attrib['NUM'] = str(self.number)
        self.header.attrib['PAGEXPOS'] = str(self.pos_x)
        self.header.attrib['PAGEYPOS'] = str(self.pos_y)
        
        # generate template for this page
        render_str = ET.tostring(self.header, encoding='utf8', method='xml').decode('utf8')
        render_str = render_str[len(basic_xml_header):]
        return render_str

class TemplatePageObject:
    _name_idx = 0

    def get_and_increment_id(self):
        current_id = TemplatePageObject._name_idx
        TemplatePageObject._name_idx += 1
        return current_id

    def __init__(self, page_obj_header, sequence_id = None):
        self.page_owner = None

        # read the xml reference, it will upadted by the page when it's positioned
        self.page_number = int(page_obj_header.attrib['OwnPage'])

        self.pos_offset_x = float(page_obj_header.attrib['XPOS'])
        self.pos_offset_y = float(page_obj_header.attrib['YPOS'])

        self.prev = int(page_obj_header.attrib['BACKITEM'])
        self.next = int(page_obj_header.attrib['NEXTITEM'])
        
        self.pos_x = 0.0
        self.pos_y = 0.0

        self.header = page_obj_header

        # unique number per object
        self.id = self.get_and_increment_id()

        # store an id based on the order they are read
        if sequence_id is not None:
            self.sequence_idx = sequence_id
        else:
            self.sequence_idx = self.id

    def set_object_position( self, base_x, base_y, idx = None):
        #update parameters of this page, so we can propagate it to the object
        # idx: the sequence idx on the document, so the links work properly
        self.pos_x = self.pos_offset_x + base_x
        self.pos_y = self.pos_offset_y + base_y

        if idx != None:
            self.sequence_idx = idx

    def render( self ):
        # connect to the right page
        self.header.attrib['OwnPage'] = str(self.page_owner.number)
        self.header.attrib['Pagenumber'] = str(self.page_owner.number)
        
        self.header.attrib['XPOS'] = str(self.pos_x)
        self.header.attrib['YPOS'] = str(self.pos_y)
        self.header.attrib['ANNAME'] = "object" + str(self.id)

        # if it's part of a sequence of liked texts it has to build the links
        if self.prev is not None:
            self.header.attrib['BACKITEM'] = str(self.prev.sequence_idx)
        else:
            self.header.attrib['BACKITEM'] = "-1"

        if self.next is not None:
            self.header.attrib['NEXTITEM'] = str(self.next.sequence_idx)
        else:
            self.header.attrib['NEXTITEM'] = "-1"
        
        obj_str = ET.tostring(self.header, encoding='utf8', method='xml').decode('utf8')
        return obj_str[len(basic_xml_header):]


def render_pages_and_objects(pages, page_width, page_height):
    pages_str = ""
    objects_str = ""
    objects_to_process = []
    current_page = 0

    # render the pages and set up the objects
    for page in pages:
        # origin for this page
        base_x_pos = 0 if (current_page % 2 == 1) else page_width
        base_y_pos = ((current_page+1) // 2) * page_height

        page.set_page_position(base_x_pos, base_y_pos, current_page)
        current_page += 1

        # add the page with the page number on the only templated text 
        page_templ = page.render()
        pages_str += Template(page_templ).render(page_number = str(page.number))

        for obj in page.page_objects:
            obj.sequence_idx = len(objects_to_process)
            objects_to_process.append(obj)
            
    # render all the objects
    for obj in objects_to_process:
        page_id = obj.page_owner.number
        page_obj_templ = obj.render()
        objects_str += Template(page_obj_templ).render(page_number = str(page_id))

    return pages_str + objects_str


def read_scribus_template(template_file_name):
    pages = []
    indices = {}

    # open the xml
    tree = ET.parse(template_file_name)
    root = tree.getroot()
    doc = list(root)[0]

    # we read all the pages on a first pass
    for elem in doc:
        if elem.tag == "PAGE":
            last_idx = len(pages)
            pages.append(TemplatePage(elem)) 
            page_xml_id = str(pages[last_idx].number)
            indices[page_xml_id] = last_idx 

    # we read all the page_objects on a second pass
    objects = []
    for elem in doc:
        if elem.tag == "PAGEOBJECT":
            # read object
            page_obj = TemplatePageObject(elem)
            objects.append(page_obj)

            print("obj: {0}: y -> {1}, p -> {2}, n -> {3}".format( 
                len(objects)-1, 
                elem.attrib['YPOS'], 
                elem.attrib['BACKITEM'], 
                elem.attrib['NEXTITEM']))

            # add to page
            page_id = indices[str(page_obj.page_number)]
            pages[page_id].add_object(page_obj)

    # create links between page objects
    object_count = len(objects)
    for obj in objects:
        if obj.next >= 0 and obj.next < object_count:
            obj.next = objects[obj.next]
        else:
            obj.next = None

        if obj.prev >= 0 and obj.prev < object_count:
            obj.prev = objects[obj.prev]
        else:
            obj.prev = None

    return pages

def render_front_cover(template_decription, pdf_config, language, base_template_path, task_path, temp_folder):
    # A. cover
    cover_descr = template_decription['cover']
    cover_template_file_name = os.path.join(
        base_template_path, cover_descr['R'])
    cover_template_right = read_template(cover_template_file_name)

    # grab and copy the image into the temp directory,
    # to have it relative to the scribus document.
    if language in pdf_config['cover_image']:
        image_file_name = pdf_config['cover_image'][language]
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
    return cover_template_right.render()


def render_back_cover(template_decription, base_template_path, current_page):
    cover_descr = template_decription['cover']
    base_y_pos = ((current_page+1) // 2) * \
        (template_decription['page_height']+40)
    cover_data = {"page_num": current_page,
                  "page_y_pos": base_y_pos,
                  "image_y_pos": base_y_pos + cover_descr['image_y_pos']}

    cover_template_file_name = os.path.join(
        base_template_path, cover_descr['L'])
    cover_template_left = read_template(cover_template_file_name)
    
    cover_end_str = cover_template_left.render(**cover_data)
    return cover_end_str
    

def render_white_page(template_decription, base_template_path, current_page):
    white_template_file_name = os.path.join(
        base_template_path, template_decription['white_page'])
    white_template = read_template(white_template_file_name)
    white_page = white_template.render(page_num=current_page)
    return white_page

def render_intro(template_decription, base_template_path, current_page):
    intro_descr = template_decription['intro']
    intro_template_file_name = os.path.join(
        base_template_path, intro_descr['filename'])
    intro_template = read_template(intro_template_file_name)

    intro_str = intro_template.render(page_0=current_page)
    intro_pages = 3
    return intro_str, intro_pages


def render_main_text(template_decription, task_description, data_base, base_template_path, current_page):
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

    main_content_str = generate_main_content(tmp_descr, task_description, taks_days)

    return main_content_str, len(taks_days)

def render_prayers(template_decription, base_template_path, current_page):
    prayers_descr = template_decription['prayers']
    prayers_template_file_name = os.path.join(
        base_template_path, prayers_descr['filename'])

    # build the template from the reference.
    prayer_pages = read_scribus_template(prayers_template_file_name)

    width = template_decription['page_width']
    height = (template_decription['page_height']+40)
    return render_pages_and_objects(prayer_pages, width, height), len(prayer_pages)

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
    base_template_path = os.path.join( session_path, "templates", "scribus", pdf_config['template'])
    template_decription_file_name = os.path.join( base_template_path, "config.json")
    template_decription = read_json_file(template_decription_file_name)

    #   Building of the leaflet itself
    #   >> Read each layer, and asemble them in a single file filling the gaps
    current_page = 0
    leaflet_content = {}

    # front cover
    #leaflet_content['cover_begining'] = render_front_cover(
    #    template_decription, pdf_config, data_base.language, base_template_path, task_path, temp_folder)
    #current_page +=1

    #leaflet_content['cover_begining'] += render_white_page (template_decription, base_template_path, current_page)
    #current_page +=1

    # B. Intro
    #leaflet_content['intro'], pages = render_intro(template_decription, base_template_path, current_page) + \
    #                           render_white_page(template_decription, base_template_path, current_page)
    # current_page += pages + 1

    # C. main text
    #leaflet_content['main_content'], pages = render_main_text(template_decription, task_description, data_base, base_template_path, current_page)
    # current_page += pages

    # D. exam
    leaflet_content['exam'] = ""
    exam_pages = 0
    current_page = current_page + exam_pages

    # E. prayers
    leaflet_content['prayers'], pages = render_prayers(template_decription, base_template_path, current_page)
    current_page += pages
    leaflet_content['prayers'] += render_white_page(template_decription, base_template_path, current_page)
    current_page += 1

    # F. final cover
    #leaflet_content['cover_end'] = render_back_cover(template_decription, base_template_path, current_page)

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
