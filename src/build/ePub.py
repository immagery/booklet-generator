import os
import shutil
import calendar

from .utils import read_template, read_json_file, copyDirectory, zip_tree
from .gs_database import build_date_key, read_list_of_days
from .namesSpecs import weekdayNumber, monthNames
from .content_utils import generateContent, getCommentStylized


def replace_in_file ( file_name, **replacement_tokens ):
	# MAIN CONTENT INDEX FILE
	
	# read template and fill it
	content_template = read_template(file_name)
	context_to_write = content_template.render(**replacement_tokens) 

	# write the context
	contentFile = open(file_name, 'w', encoding="utf-8")
	contentFile.write( context_to_write )
	contentFile.close()	

def build_epub (task_description, data_base, task_path, session_path, out_path) :

	epub_config = task_description['mediums']['epub']
	if "template" not in epub_config:
		print("there is no template defined for the ePub work!")
		return

	# read the configuration file for the template
	base_template_path = os.path.join( session_path, "templates", "epub", epub_config['template'])
	template_decription_file_name = os.path.join( base_template_path,"config.json")
	template_decription = read_json_file(template_decription_file_name)

	# set up the template in order to fill it with the booklet content
	temp_folder = os.path.join(out_path, "temp")
	epub_output_dir = os.path.join( temp_folder, "epub_build")

	#if os.path.exists(epub_output_dir):
	#	shutil.rmtree(epub_output_dir)
	os.makedirs(epub_output_dir, exist_ok=True)
	
	# copy the template
	copyDirectory( os.path.join( base_template_path, template_decription["ePub_build_template"]) , epub_output_dir)

	# MAIN CONTENT INDEX FILE
	main_content = os.path.join(epub_output_dir, template_decription["contentFile"])
	id_code = str(task_description["first_day"]) + str(task_description["first_month"]) + str(task_description["first_year"])
	replace_in_file(main_content, 
					title_ipray_booklet = task_description['name'], 
					booklet_id = task_description['name'] + id_code)

	# toc file
	toc_file = os.path.join(epub_output_dir, template_decription["tocFile"])
	replace_in_file(toc_file, 
					title_ipray_booklet = task_description['name'], 
					booklet_id = task_description['name'] + id_code)

	#table of contents
	table_of_contents = os.path.join(epub_output_dir, template_decription["tableOfContentFile"])
	
	# get days for the app
	days_list = read_list_of_days( task_description["days_list"] )
	task_days = data_base.produce_days_from_list( days_list )

	processed_tasks = []

	months_info = {}
	for task in task_days:
		if task.version > 0:
			continue

		if task.blank:
			continue

		task_processed = generateContent(task, len(processed_tasks), language = data_base.language)
		processed_tasks.append( task_processed )

		month_string = task.getMonthString(data_base.language)
		weekday_number = calendar.weekday(task.year, task.month, task.day) + 1
		if month_string not in months_info.keys():
			months_info[month_string] = {}
			months_info[month_string]['year'] = task.year
			months_info[month_string]['first_day'] = task.day
			months_info[month_string]['first_day_week'] = weekday_number
			weeks = calendar.monthcalendar(task.year, task.month)
			months_info[month_string]['calendar_in_weeks'] = weeks
			months_info[month_string]['days'] = {}
			#print( task.year, task.day, weekday_number )
		else:
			if months_info[month_string]['first_day'] > task.day:
				months_info[month_string]['first_day'] = task.day
				months_info[month_string]['first_day_week'] = weekday_number

		months_info[month_string]['days'][task.day] = task_processed

	replace_in_file(table_of_contents, months = months_info)

	meditations_content = os.path.join(epub_output_dir, template_decription["meditationsContentFile"])
	replace_in_file(meditations_content, tittle =  task_description['name'],  days = processed_tasks)

	# copy the right cover
	cover_file = os.path.join(task_path, epub_config["cover"][data_base.language])
	logo_file = os.path.join(task_path, epub_config["logo"])
	shutil.copyfile(cover_file, os.path.join(epub_output_dir, template_decription["finalCoverFile"]))
	shutil.copyfile(logo_file,  os.path.join(epub_output_dir, template_decription["finalLogoFile"]))

	#compress the set as an ePub File
	zip_tree(epub_output_dir, os.path.join(temp_folder, "{0}.epub".format(task_description['name'])))


def build_mobi (*args, **kargs) :
	print("Build mobi!!!!")