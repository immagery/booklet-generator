

#import os
#os.environ['PYTHONPATH'] = os.path.dirname(os.path.realpath(__file__))

#import iPraybuild
#import test_suite

import xml.etree.ElementTree as ET
tree = ET.parse('C:\Users\me\Documents\dev\iPray\scribus_first_test_template.sla')
root = tree.getroot()

document = root.find('DOCUMENT')
if document is None:
    raise Exception("This file doesn't have the right format")

page_items = document.findall("PAGE")

document.append( page_items[0] )

print page_items
#for child in root:
#    print child.tag, child.attrib

tree.write('C:\Users\me\Documents\dev\iPray\scribus_first_test_modified.sla')
