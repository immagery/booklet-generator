import xml.etree.ElementTree as ET

tree = ET.parse('C:\\dev\\iPray\\data\\templates\\scribus\\printable-booklet\\base_booklet_cleanup.sla')
root = tree.getroot()

_PAGE_TAG = "PAGE"



doc = get_child(root, 'DOCUMENT')
print("Analizing doc:")

# tags
tags = set()
for item in doc:
    tags.add(item.tag)
print("All tags: {}".format(tags))

prev= 0
for page in get_child(doc, _PAGE_TAG, all_items = True):
    posy = float(page.attrib['PAGEYPOS']) 
    print(posy - prev)
    prev = posy

# styles
# color



# build a new xml

'''
a = ET.Element('a')
b = ET.SubElement(a, 'b')
c = ET.SubElement(a, 'c')
d = ET.SubElement(c, 'd')
ET.dump(a)
'''