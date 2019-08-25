from jinja2 import Template

def read_template(file_name):
    try:
        template_xml = open(file_name).read()
    except:
        raise Exception("The template file {} can't be opened or read".format(file_name))

    return Template( template_xml )


def build_pdf (*args, **kargs) :
	print("Build PDFFFFF!!!!")