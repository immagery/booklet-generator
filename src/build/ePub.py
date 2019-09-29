
import os
import shutil

from .utils import read_template, read_json_file

def replace_in_file ( file_name, **replacement_tokens ):
	# MAIN CONTENT INDEX FILE
	contentFile = open(file_name, 'w+')
	content_template = read_template(contentFile.read())
	contentFile.write(content_template.render(**replacement_tokens) )
	contentFile.close()	

def build_epub (task_description, data_base, task_path, session_path, out_path) :

	epub_config = task_description['mediums']['epub']
	if "template" not in epub_config:
		print("there is no template defined for the ePub work!")
		return

	# read the configuration file for the template
	base_template_path = os.path.join( session_path, "templates", "epub")
	template_decription_file_name = os.path.join( base_template_path, "config.json")
	template_decription = read_json_file(template_decription_file_name)

	# set up the template in order to fill it with the booklet content
	temp_folder = os.path.join(out_path, "temp")
	os.makedirs(temp_folder, exist_ok=True)

	# copy the template
	epub_output_dir = os.path.join( temp_folder, "epub_build")
	utils.copyDirectory( os.path.join( base_template_path, template_decription["ePub_build_template"]) , epub_output_dir)

	# MAIN CONTENT INDEX FILE
	file_name = os.join(epub_output_dir, template_decription["contentFile"])
	id_code = str(task_description["first_day"]) + str(task_description["first_month"]) + str(task_description["first_year"]) + str(task_description["text_count"]) 
	replace_strings = { "title-ipray-booklet" : task_description['name'], 
						"booklet-id" : task_description['name'] + id_code }
	replace_in_file(file_name, replace_strings)

	# toc file
	file_name = os.join(epub_output_dir, template_decription["tocFile"])
	replace_in_file(file_name, replace_strings)

	#table of contents
	replace_strings["iPrayTableOfContents"] = buildMonthHTML(task_description["first_month"], task_description["first_year"], data_base)
	
	file_name = os.join(epub_output_dir, template_decription["tableOfContentFile"])
	replace_in_file(file_name, replace_strings)

	print("Build epub!!!!")



def build_mobi (*args, **kargs) :
	print("Build mobi!!!!")