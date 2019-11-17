import os
import shutil

from .utils import read_template, read_json_file, copyDirectory, zip_tree
from .gs_database import build_date_key, read_list_of_days
from .namesSpecs import weekdayNumber
from .content_utils import generateContent, getCommentStylized


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
	copyDirectory( os.path.join( base_template_path, template_decription["ePub_build_template"]) , epub_output_dir)

	# MAIN CONTENT INDEX FILE
	main_content = read_template( os.path.join(epub_output_dir, template_decription["contentFile"]) )
	id_code = str(task_description["first_day"]) + str(task_description["first_month"]) + str(task_description["first_year"]) + str(task_description["text_count"])
	replace_in_file(main_content, title_ipray_booklet = task_description['name'], booklet_id = task_description['name'] + id_code)

	# toc file
	toc_file = os.path.join(epub_output_dir, template_decription["tocFile"])
	replace_in_file(toc_file, title_ipray_booklet = task_description['name'])

	#table of contents
	table_of_contents = read_template( os.path.join(epub_output_dir, template_decription["tableOfContentFile"]) )
	
	# get days for the app
	days_list = read_list_of_days( task_description["days_list"] )
	task_days = data_base.produce_days_from_list( days_list )

	processed_tasks = []
	for task in task_days:
		if task.version > 0:
			continue
		day_content = generateContent(task, len(processed_tasks))

	weekday_num = weekdayNumber[data_base.language][task_description["first_weekday_day"]]
	grey_days = [ i for i in range(1, weekday_num-1) ] if weekday_num>1 else []

	replace_in_file(table_of_contents, 
					month = str(task_description["first_month"]), 
					year = str(task_description["first_year"]), 
					calendar_filling_days = grey_days, 
					calendar_days = day_content)

	meditations_content = read_template( os.path.join(epub_output_dir, template_decription["meditationsContentFile"]) )
	replace_in_file(meditations_content, tittle =  task_description['name'],  calendar_days = day_content)

	# copy the right cover
	cover_file = os.path.join(task_path, epub_config["cover_file"][data_base.language])
	logo_file = os.path.join(task_path, epub_config["logo_file"][data_base.language])
	shutil.copyfile(cover_file, task_description["finalCoverFile"])
	shutil.copyfile(logo_file, task_description["finalLogoFile"])

	#compress the set as an ePub File
	zip_tree(epub_output_dir, os.path.join(temp_folder, "{0}.epub".format(task_description['name'])))

	print("Build epub!!!!")



def build_mobi (*args, **kargs) :
	print("Build mobi!!!!")