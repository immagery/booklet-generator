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

def render_pages_and_objects( pages, page_width, page_height, 
                              page_number_offset = 0, object_id_offset = 0, 
                              filling = None):
    pages_str = ""
    objects_str = ""
    
    if filling == None:
        filling = {}

    # render the pages and set up the objects
    objects_to_process = []
    current_page = page_number_offset
    for page in pages:
        # origin for this page
        base_x_pos = 0 if (current_page % 2 == 1) else page_width
        base_y_pos = ((current_page+1) // 2) * page_height

        page.set_page_position(base_x_pos, base_y_pos, current_page)
        current_page += 1

        # add the page with the page number on the only templated text 
        page_templ = page.render()
        filling['page_number'] = str(page.number)
        pages_str += Template(page_templ).render( **filling )

        for obj in page.page_objects:
            obj.sequence_idx = len(objects_to_process)+object_id_offset
            objects_to_process.append(obj)
            
    # render all the objects
    for obj in objects_to_process:
        page_id = obj.page_owner.number
        page_obj_templ = obj.render()
        filling['page_number'] = str(page_id)
        objects_str += Template(page_obj_templ).render( **filling )

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

def restore_image_link( pages, code_str, code_image ):
    # replace the image paths to point to the right place (again, it's generic!!!)
    for page in pages:
        for obj in page.page_objects:
            # if it's image, look for path
            if int(obj.header.attrib['PTYPE']) == 2 and 'PFILE' in obj.header.attrib:
                if code_str in obj.header.attrib['PFILE']:
                    obj.header.attrib['PFILE'] = code_image

'''
def build_prayer_pages(template_decription, base_template_path):
    prayers_descr = template_decription['prayers']
    prayers_template_file_name = os.path.join( base_template_path, prayers_descr['filename'] )

    # build the template from the reference.
    return read_scribus_template(prayers_template_file_name)

def build_cover_pages(template_decription, base_template_path, images):
    cover_descr = template_decription['cover']
    cover_template_file_name = os.path.join( base_template_path, cover_descr['filename'])

    # build the template from the reference.
    cover_pages = read_scribus_template(cover_template_file_name)

    code_image = cover_descr['rel_path'][1]
    if code_image in images:
        restore_image_link(cover_pages, cover_descr['rel_path'][0], images[code_image] )
    else:
        print("The code image is not defined properly")

    return cover_pages

def build_intro_pages(template_decription, base_template_path, images):
    intro_descr = template_decription['intro']
    intro_template_file_name = os.path.join( base_template_path, intro_descr['filename'] )
    intro_pages = read_scribus_template(intro_template_file_name)

    code_image = intro_descr['rel_path'][1]
    if code_image in images:
        restore_image_link(intro_pages, intro_descr['rel_path'][0], images[code_image] )
    else:
        print("The code image is not defined properly")

    # build the template from the reference.
    return intro_pages

def build_exam_pages(template_decription, base_template_path, images):
    descr = template_decription['exam']
    template_file_name = os.path.join( base_template_path, descr['filename'] )
    pages = read_scribus_template(template_file_name)

    code_image = descr['rel_path'][1]
    if code_image in images:
        restore_image_link(pages, descr['rel_path'][0], images[code_image] )
    else:
        print("The code image is not defined properly")

    # build the template from the reference.
    return pages
'''

def build_generic_pages(descr, base_template_path, images = None):
    ## read the template pages
    template_file_name = os.path.join( base_template_path, descr['filename'] )
    pages = read_scribus_template(template_file_name)

    # replace image paths if required
    if images != None and 'images' in descr: 
        code_image = descr['images'][1]
        if code_image in images:
            restore_image_link(pages, descr['images'][0], images[code_image] )
        else:
            print("The code image is not defined properly.")

    return pages


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

    # copy all the images needed from the task and the template
    image_references = {}
    for image_code, image_descr in pdf_config['images'].items():
        if data_base.language in image_descr:
            image_file_name = image_descr[data_base.language]
        else:
            image_file_name = image_descr['english']

        image_file_path = os.path.join(task_path, image_file_name)
        try:
            temp_image_file = os.path.join(temp_folder, "pdf_{0}_image.jpg".format(image_code))
            copyfile(image_file_path, temp_image_file)
            image_references[image_code] = temp_image_file
        except IOError as e:
            print(
                "Unable to copy the cover image to generate the pdf. [{0}]".format(e))

    for image_code, image_descr in template_decription['images'].items():
        image_file_path = os.path.join(base_template_path, image_descr)
        try:
            temp_image_file = os.path.join(temp_folder, "pdf_{0}_image.jpg".format(image_code))
            copyfile(image_file_path, temp_image_file)
            image_references[image_code] = temp_image_file
        except IOError as e:
            print(
                "Unable to copy the cover image to generate the pdf. [{0}]".format(e))


    #   Building of the leaflet itself
    #   >> Read each layer, and asemble them in a single file filling the gaps
    leaflet_content = {}

    # front cover
    cover_pages = build_generic_pages(template_decription['cover'], base_template_path, image_references)

    # B. Intro
    intro_pages = build_generic_pages(template_decription['intro'], base_template_path, image_references)
    #leaflet_content['intro'], pages = render_intro(template_decription, base_template_path, current_page) + \
    #                           render_white_page(template_decription, base_template_path, current_page)
    # current_page += pages + 1

    # C. main text
    #leaflet_content['main_content'], pages = render_main_text(template_decription, task_description, data_base, base_template_path, current_page)
    # current_page += pages

    # D. exam
    leaflet_content['exam'] = ""

    # E. prayers
    prayer_pages = build_generic_pages(template_decription['prayers'], base_template_path)
    
    page_composition = cover_pages[0:2]
    page_composition.extend(intro_pages)
    page_composition.extend(prayer_pages)
    page_composition.extend(cover_pages[2:])

    width = template_decription['page_width']
    height = (template_decription['page_height']+40)
    doc_str = render_pages_and_objects(page_composition, width, height)

    # copy base label
    for labels in template_decription['base_leaflet_labels']:
        leaflet_content[labels] = template_decription[labels]

    # overwrite those needed
    leaflet_content['page_count'] = len(page_composition)
    leaflet_content['content'] = doc_str

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
