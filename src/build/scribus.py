from jinja2 import Template

import os
from shutil import copyfile
import copy 

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

    def __init__(self, page_header = None, sub_pages = None, ref_pos_x=100.00062992126, ref_pos_y=20.0012598425197):

        # Current position of the page
        self.pos_x = 0.0
        self.pos_y = 0.0

        # where the origin of the page is related to the frame
        self.ref_pos_x = ref_pos_x
        self.ref_pos_y = ref_pos_y

        # to compute all the objects in reference to the current page
        if page_header != None:
            self.number = int(page_header.attrib['NUM'])
            self.offset_x = float(page_header.attrib['PAGEXPOS'])-self.ref_pos_x
            self.offset_y = float(page_header.attrib['PAGEYPOS'])-self.ref_pos_y

        # reference to the original xml description
        # A way to store variables (L & R)
        self.sub_pages = sub_pages
        self.header = page_header
        self.content = None

        # list of objects part of this page
        self.page_objects = []

    def add_object(self, page_obj):
        # localise and add an object to the list
        page_obj.pos_offset_x = page_obj.pos_offset_x - self.offset_x
        page_obj.pos_offset_y = page_obj.pos_offset_y - self.offset_y

        self.page_objects.append(page_obj)
        page_obj.page_owner = self

    def set_page_position( self, base_x, base_y, page_number):
        if self.sub_pages != None:
            # select the variant
            if (page_number % 2 == 1) :
                page = self.sub_pages['right']
            else:
                page = self.sub_pages['left']
            
            page.set_page_position(base_x, base_y, page_number)

            # copy all the stuff from the edited page to the parent page.
            self.header = page.header
            self.page_objects = page.page_objects
            self.ref_pos_x = page.ref_pos_x
            self.ref_pos_y = page.ref_pos_y
            page.content = self.content

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
        obj_str = obj_str[len(basic_xml_header):]

        # fill the template with the content registered if any
        if self.page_owner.content != None:
            # prepare the template
            if 'replacement_chain' in self.page_owner.content:
                for replacement in self.page_owner.content['replacement_chain']:
                    if replacement[0] in obj_str:
                        obj_str = obj_str.replace(replacement[0], replacement[1])

            # fill the template
            obj_str = Template(obj_str).render( **self.page_owner.content )
            
        return obj_str

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
            pages.append(TemplatePage( page_header = elem)) 
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

def build_main_pages(template_decription, task_description, data_base, base_template_path):
    ## read the template pages
    descr = template_decription['main_content']
    template_file_name = os.path.join( base_template_path, descr['filename'] )
    pages = read_scribus_template(template_file_name)
    left_page = pages[descr['left_page']]
    right_page = pages[descr['right_page']]

    hybrid_page = TemplatePage( sub_pages={'left' : left_page, 'right': right_page} )
    
    first_date = build_date_key(
        task_description["first_day"],
        task_description["first_month"],
        task_description["first_year"])

    taks_days = data_base.produce_days( first_date, task_description['text_count'])

    content_pages = []
    for day in taks_days:
        page_data = {}

        page_data['gospel'] = day.gospel.replace("\"", "&quot;")
        page_data['comment'] =  build_comment_items( day.comment,
                                descr['comment_item'], 
                                template_decription['character_style_templates'])
        page_data['onomastica'] = day.onomastic
        page_data['date'] = day.getFullStringDay()
        page_data['quote'] = day.quote

        page_data['replacement_chain'] = descr['replacement_chain']

        # copy the template and add the new content, it will be rendered
        # when we know if the page goes in the left or the right
        new_page = copy.deepcopy(hybrid_page)
        new_page.content = page_data
        content_pages.append(new_page)

    return content_pages
    

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
    page_composition = cover_pages[0:2]

    # B. Intro
    intro_pages = build_generic_pages(template_decription['intro'], base_template_path, image_references)
    page_composition.extend(intro_pages)
    
    # C. main text
    main_pages = build_main_pages(template_decription, task_description, data_base, base_template_path)
    page_composition.append( copy.deepcopy(cover_pages[1]) )
    page_composition.extend(main_pages)

    # D. exam
    exam_pages = build_generic_pages(template_decription['exam'], base_template_path, image_references)
    page_composition.append(exam_pages[0])

    # E. prayers
    prayer_pages = build_generic_pages(template_decription['prayers'], base_template_path)
    page_composition.extend(prayer_pages)

    # closing cover
    if page_composition % 2 == 0:
        page_composition.append( copy.deepcopy(cover_pages[1]) )
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
