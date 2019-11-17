import os
from .utils import read_json_file, read_template
from .gs_database import build_date_key, read_list_of_days

from .content_utils import generateContent, getCommentStylized

def fillXhtmlContents( task_description, data_base, task_path, session_path, app_out_folder ):
	
	app_config = task_description['mediums']['android']
	if "template" not in app_config:
		print("there is no template defined for the PDF work!")
		return
	
	base_template_path = os.path.join( session_path, "templates", "android", app_config['template'])
	print("template to read: " + base_template_path)

	day_template = read_template(base_template_path)
	
	# get days for the app
	days_list = read_list_of_days( task_description["days_list"] )
	task_days = data_base.produce_days_from_list( days_list )

	page_id = 0
	for day in task_days:		
		dailyContent = generateContent(day, page_id, day_template)
		
		if day.version == 0:
			file_name = os.path.join(app_out_folder, "[{id}]{day}-{month}.html".format( id = page_id, day=day.day, month = day.month ))
		else:
			file_name = os.path.join(app_out_folder, "[{id}]{day}-{month}_{v_id}.html".format( id = page_id, day=day.day, month = day.month, v_id = day.version ))

		ext_file = open(file_name, 'w', encoding="utf-8")
		ext_file.write(dailyContent)
		ext_file.close()

		page_id += 1

	return len(task_days)

def build_app(task_description, data_base, task_path, session_path, out_path):
	
	app_out_folder = os.path.join(out_path, "androidApp")
	os.makedirs(app_out_folder, exist_ok=True)

	num_of_pages = fillXhtmlContents( task_description, data_base, task_path, session_path, app_out_folder )

	print("Builded {0} days!".format(num_of_pages)) 
	print("Congratulations: app files produced!!!")