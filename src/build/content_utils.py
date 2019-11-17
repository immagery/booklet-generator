
def generateContent(day_data, content_id, template = None):
	contents = {}
	contents['day_tittle'] = day_data.code
	contents['page_number'] = content_id
	contents['day_string'] = day_data.getFullStringDay()
	#contents['day_of_the_week'] = day_data.getStringWeekDay()
	contents['saint'] = day_data.onomastic
	contents['citation'] = day_data.quote
	contents['gospel'] = day_data.gospel
	contents['subcontent'] = getCommentStylized(day_data.comment)
	contents['link'] = "page_{0}_{1}".format(content_id,day_data.code)
	contents['day_number_string'] = day_data.get_string_day()
	contents['day_number'] = day_data.day

	if template is not None:
		page_text = template.render(**contents)
		return page_text
	else:
		return contents

def getCommentStylized(comment):
	content = ""
	for p in comment:
		content = content + "<p>"
		for b in p:
			if b[0] == 'normal':
				content = content + b[1]
			elif b[0] == 'italic':
				content = content + '<i>' + b[1] + '</i>'
			elif b[0] == 'boldItalic':
				content = content + '<b><i>' + b[1] + '</i></b>'
			elif b[0] == 'bold':
				content = content + '<b>' + b[1] + '</b>'
			else:
				print('''\n\n\n\n\n\nYou haven't considered this key (%s) for formating''' % b[0])
		content = content + "</p>\n"
	return content