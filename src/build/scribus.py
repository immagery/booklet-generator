import os
from shutil import copyfile
import copy 

from jinja2 import Template

from .utils import read_json_file, read_template
from .gs_database import build_date_key, read_list_of_days

from collections import OrderedDict

import xml.etree.ElementTree as ET

basic_xml_header = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
BYPASS_TEMPLATE_TAGS = ['DocItemAttributes', 'NotesStyles', 'STYLE', 'Sections', 'COLOR', 'TablesOfContents', 'LAYERS', 'HYPHEN', 'CellStyle', 'MASTERPAGE', 'TableStyle', 'PageSets', 'CHARSTYLE', 'CheckProfile', 'PDF', 'Printer']

def get_child(item, children, all_items = False):
    """ Search for element/s children """
    collected_items = []
    for child in item:
        if child.tag == children:
            if all_items:
                collected_items.append(child)
            else:
                return child
    return collected_items

def crate_from_header(doc):
    new_doc = ET.Element(doc.tag)
    for key in doc.attrib:
        new_doc.attrib[key] = doc.attrib[key]
    return new_doc

def copy_header(doc, new_doc):
    for key in doc.attrib:
        new_doc.attrib[key] = doc.attrib[key]

def is_next_left(pages_list):
    return len(pages_list) % 2 == 0

class Paragraph:
    STYLE_ATTR = 'PARENT'
    PARAGRAPH_TAG = 'para'
    END_TAG = 'trail'

    def __init__(self, style, end = False):
        self.style = style
        self.end = end

    def add_items(self, parent):
        if self.end:
            xml_item = ET.Element(self.END_TAG)
        else:
            xml_item = ET.Element(self.PARAGRAPH_TAG)

        xml_item.attrib[self.STYLE_ATTR] = self.style
        parent.append(xml_item)
    
class Itext:
    # attributes
    STYLE_ATTR = 'CPARENT'
    CHARACTER_ATTR = 'CH'
    TEXT_TAG = 'ITEXT'

    def __init__(self, style, pstyle = None, text = None):
        self._text = ET.Element(self.TEXT_TAG)
        self._text.attrib[self.STYLE_ATTR] = style
        self._text.attrib[self.CHARACTER_ATTR] = text or ""        
        self._paragraph = Paragraph(pstyle) if pstyle else None

    def add_items(self, parent):
        if self.CHARACTER_ATTR not in self._text.attrib:
            raise Exception("this piece of text is not well built")
        
        if self._paragraph:
            self._paragraph.add_items(parent)

        parent.append(self._text)
        return self._text

class ContentStory:
    STORY_TAG = "StoryText"
    DEFAULT_STYLE_TAG = "DefaultStyle"

    def __init__(self, xml_item = None, content = None):
        self.xml_item = xml_item
        if xml_item is not None:
            return

        # If we have to build a contents xml element
        self._style =  ET.Element(self.DEFAULT_STYLE_TAG)
        self._style.attrib[Paragraph.STYLE_ATTR] = "normal"

        self._text = []
        self._elements = {}

        if not content:
            return

        saint_item = Itext( style = "santo_title", text = content.onomastic)
        self._elements['saint'] = saint_item
        self._text.append(saint_item)

        day_item = Itext( style = "santo_title", pstyle = "normal", text = content.getFullStringDay())
        self._elements['day'] = day_item
        self._text.append(day_item)

        versiculo_item = Itext( style = "versiculo", pstyle = "Title", text = content.quote)
        self._elements['versiculo'] = versiculo_item
        self._text.append(versiculo_item)

        #gospel
        gospel_item = Itext( style = "italic", pstyle = "gospel", text = content.gospel.replace("\"", "&quot;") )
        self._text.append(gospel_item)

        # comments
        # reflexion, reflexion-italic, reflexion-black
        gospel_item = Itext( style = "reflexion", pstyle = "normal")
        self.build_content_paragraphs(content.comment, content.style_translation)

        trail = Paragraph( style = "normal", end = True)
        self._text.append( trail )

    def build_content_paragraphs(self, comment, style_translation):
        for paragraph in comment:
            paragraph_style = Paragraph( style = "normal" )
            self._text.append(paragraph_style)

            for elem in paragraph:
                text = elem[1].replace("\"", "&quot;")

                style = elem[0] if elem[0] in style_translation else "reflexion"
                comment_item = Itext( style = style, text = text )

                self._text.append(comment_item)

    def add_items(self, parent):
        parent.append(self.get_xml_item())

    def get_xml_item(self):
        if self.xml_item is not None:
            print("por aqui")
            return self.xml_item

        story_item = ET.Element(self.STORY_TAG)
        for item in self._text:
            item.add_items(story_item)

        return story_item

class Page:
    def __init__(self, page_xml = None, page_obj_xml = None, content = None):

        # Current position of the page
        self.pos_x = 0.0
        self.pos_y = 0.0

        # to compute all the objects in reference to the current page
        self.page_xml = page_xml
        if page_xml != None:
            self.number = int(page_xml.attrib['NUM'])
            self.pos_x = float(page_xml.attrib['PAGEXPOS'])
            self.pos_y = float(page_xml.attrib['PAGEYPOS'])
            self.borders = [float(page_xml.attrib['BORDERTOP']),
                            float(page_xml.attrib['BORDERRIGHT']),
                            float(page_xml.attrib['BORDERBOTTOM']),
                            float(page_xml.attrib['BORDERLEFT'])]

        # list of objects part of this page
        self.page_objects = []

        if content and page_obj_xml:
            page_obj = PageObject(xml_item = page_obj_xml, owner_page = self, content = content)
            self.page_objects.append(page_obj)

    def add_object(self, page_obj):
        self.page_objects.append(page_obj)

    def add_items(self, parent):
        # compute position based on page number
        page_xml = crate_from_header(self.page_xml)
        page_xml.attrib['NUM'] = str(self.number)
        page_xml.attrib['PAGEXPOS'] = str(self.pos_x)
        page_xml.attrib['PAGEYPOS'] = str(self.pos_y)
        parent.append(page_xml)

class PageObject:
    _name_idx = 0

    def get_and_increment_id(self):
        current_id = PageObject._name_idx
        PageObject._name_idx += 1
        return current_id

    def __init__(self, xml_item, owner_page, content = None):
        self.owner_page = owner_page
        self.owner_page.add_object(self)
        # read the xml reference, it will upadted by the page when it's positioned

        if xml_item is not None:
            self.page_number = int(xml_item.attrib['OwnPage'])

            self.pos_x = float(xml_item.attrib['XPOS']) - owner_page.pos_x
            self.pos_y = float(xml_item.attrib['YPOS']) - owner_page.pos_y

            self.prev = int(xml_item.attrib['BACKITEM'])
            self.next = int(xml_item.attrib['NEXTITEM'])
        
            self.id = int(xml_item.attrib['ItemID'])

            self.xml_item = xml_item

        # unique number per object
        self._new_id = self.get_and_increment_id()

        # store an id based on the order they are read
        #if sequence_id is not None:
        #    self.sequence_idx = sequence_id
        #else:
        self.sequence_idx = self._new_id

        self.content = None
        if content:
            self.content = ContentStory(content = content)
        else:
            if xml_item is not None:
                self.content = ContentStory(xml_item = get_child(xml_item, 'StoryText'))
            else:
                raise Exception("there should be some content or xml item")

    def add_items(self, parent):
        # compute position based on page position
        page_obj_xml = crate_from_header(self.xml_item)
        page_obj_xml.attrib['OwnPage'] = str(self.owner_page.number)
        page_obj_xml.attrib['XPOS'] = str(self.pos_x + self.owner_page.pos_x)
        page_obj_xml.attrib['YPOS'] = str(self.pos_y + self.owner_page.pos_y)
        
        if self.content:
            content = self.content.get_xml_item()
            if not isinstance(content, list):
                page_obj_xml.append(content)
                parent.append(page_obj_xml)
            else:
                print(self.xml_item)
            


class Document:
    def __init__( self, xml_item ):
        root = xml_item.getroot()
        self._root = crate_from_header(root)
        self._doc = crate_from_header(list(root)[0])
        self._root.append(self._doc)

        self.pages = []

        self.page_width = float(self._doc.attrib['PAGEWIDTH'])
        self.page_height = float(self._doc.attrib['PAGEHEIGHT'])
        self.page_borders = ['BORDERTOP','BORDERRIGHT', 'BORDERBOTTOM', 'BORDERLEFT']
        for idx in range(len(self.page_borders)):
            self.page_borders[idx] = float(self._doc.attrib[self.page_borders[idx]])

        self.orig_x = float(self._doc.attrib['MAJGRID'])
        self.orig_y = float(self._doc.attrib['MINGRID'])
    
    def get_page_pos(self, number):
        """position for the pages starting from 0"""
        return self.orig_x, self.orig_y + (self.orig_y*2+self.page_height)*number

    def get_doc(self):
        return self._doc
    
    def dump_to_xml(self, filename = None):
        # xml header
        xml_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        xml_string += ET.tostring(self._root, encoding="unicode")

        if filename:
            out_file = open(filename, "w")
            out_file.write(xml_string)
            out_file.close()
        
        return xml_string

    def add_xml_item(self, xml_item):
        self._doc.append(xml_item)

    def add_page(self, page):
        page_position = len(self.pages)
        page.pos_x, page.pos_y = self.get_page_pos(page_position)
        page.number = page_position
        self.pages.append(page)
        page.add_items(self._doc)

    def add_page_object(self, page_obj):
        page_obj.add_items(self._doc)

    def set_attr(self, label, value):
        self._doc.attrib[label] = value


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
    other_elements = []
    page_ids = {}

    # open the xml
    tree = ET.parse(template_file_name)
    root = tree.getroot()
    doc = list(root)[0]

    # we read all the pages on a first pass
    for elem in doc:
        if elem.tag == "PAGE":
            new_page = Page(elem)
            pages.append(new_page)
            page_ids[elem.attrib['NUM']] = new_page

    # we read all the page_objects on a second pass
    objects = []
    object_ids = {}
    for elem in doc:
        if elem.tag == "PAGEOBJECT":
            if elem.attrib['OwnPage'] not in page_ids:
                continue
            owner_page = page_ids[elem.attrib['OwnPage']]
            # read object
            page_obj = PageObject(xml_item = elem, owner_page = owner_page)
            objects.append(page_obj)
            object_ids[int(elem.attrib['ItemID'])] = page_obj

        elif elem.tag != "PAGE":
            other_elements.append(elem)

    # create links between page objects
    for obj in objects:
        if obj.next >= 0:
            obj.next = object_ids[obj.next]
        else:
            obj.next = None

        if obj.prev >= 0:
            obj.prev = object_ids[obj.prev]
        else:
            obj.prev = None

    return pages, other_elements

def restore_image_link( pages, code_str, code_image ):
    # replace the image paths to point to the right place (again, it's generic!!!)
    for page in pages:
        for obj in page.page_objects:
            # if it's image, look for path
            if int(obj.header.attrib['PTYPE']) == 2 and 'PFILE' in obj.header.attrib:
                if code_str in obj.header.attrib['PFILE']:
                    obj.header.attrib['PFILE'] = code_image

def build_main_pages(reference_page, task_description, data_base, template_decription):

    # use xml page and object as reference
    # get objet and use that to set the position, it will have to be adjusted if it's left or right
    
    days_list = read_list_of_days( task_description["days_list"] )
    task_days = data_base.produce_days_from_list( days_list )
    
    ref_page_xml = reference_page.page_xml
    ref_page_obj_xml = reference_page.page_objects[0].xml_item

    content_pages = []
    for day in task_days:
        if day.code == 'white':
            # TODO: support for month breaking pages...
            print("there should be a white page at this point")
            continue
        
        day.style_translation = template_decription['character_style_templates']
        page = Page(page_xml = ref_page_xml, page_obj_xml = ref_page_obj_xml, content = day)
        content_pages.append(page)

    return content_pages

def build_scribus_leaflet(task_description, data_base, task_path, session_path, temp_folder):
    
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

    template_file_name = os.path.join( base_template_path, template_decription['main_content']['filename'] )
    pages, other_elements = read_scribus_template(template_file_name)

    # add intro
    final_pages = pages[:2]

    # create_content
    final_pages += build_main_pages(pages[3], task_description, data_base, template_decription)

    # pick left or right for the exam
    if is_next_left(final_pages):
        final_pages.append(pages[4])
    else:
        final_pages.append(pages[5])

    # add the end of the booklet (prayers)
    final_pages += pages[6:]

    print("final pages count ", len(final_pages))

    new_document = Document(ET.parse(template_file_name))

    # add all the elements that in the template that are not pages    
    for item in other_elements:
        new_document.add_xml_item(item)

    # add the new composed pages
    for page in final_pages:
        new_document.add_page(page)

    # add the page objects for all those pages
    for page in final_pages:
        for obj in page.page_objects:
            new_document.add_page_object(obj)

    new_document.set_attr('ANZPAGES', str(len(final_pages)+1))

    # save new file
    temp_file_name = os.path.join(temp_folder, "result_booklet.sla")
    print("Result: {}".format(temp_file_name))
    new_document.dump_to_xml(temp_file_name)


def build_print_pdf(task_description, data_base, task_path, session_path, out_path):
    raise Exception("Print pdf not implemented yet")


def build_pdf(task_description, data_base, task_path, session_path, out_path):
    """ Builds all the pdf configurations given the task_description
    """
    
    pdf_config = task_description['mediums']['pdf']
    if "template" not in pdf_config:
        print("there is no template defined for the PDF work!")
        return

    # read the configuration file for the template
    base_template_path = os.path.join( session_path, "templates", "scribus", pdf_config['template'])
    template_decription_file_name = os.path.join( base_template_path, "config.json")
    template_decription = read_json_file(template_decription_file_name)

    temp_folder = os.path.join(out_path, "temp")
    os.makedirs(temp_folder, exist_ok=True)

    build_scribus_leaflet(task_description, data_base, task_path, session_path, temp_folder)

    # run the conversion of into a final pdf
    '''
    pdf_filename = "iPray{0}_{1}.pdf".format(task_description['name'], data_base.language)
    conversion_params = { "scribus_exec" : template_decription['scribus_exec'],
                          "python_script" : os.path.join( session_path, "templates", "scribus", template_decription['conversion_script']),
                          "scribus_file" : temp_file_name,
                          "dest_file" : os.path.join(temp_folder, pdf_filename) }

    print('{scribus_exec} -g -py {python_script} --python-arg {dest_file} {scribus_file}'.format( **conversion_params ))
    os.system('{scribus_exec} -g -py {python_script} --python-arg {dest_file} {scribus_file}'.format( **conversion_params ))
    '''

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
