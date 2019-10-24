#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 

Convert a document to a PDF

Run with a command like
	/c/Program\ Files/Scribus\ 1.5.5/Scribus.exe -ns -g  -py src/build/export_pdf_from_file.py ./iPrayNovember19_bleed3mm.pdf 44 iPrayNovember True -- data/export/english/2019/november/pdf/temp/result_booklet.sla


You can set any "pdf" attribute with "-pa -attribute value".

Tested with scribus 1.5.1 r20382

Author: William Bader, Director of Research and Development, SCS, http://www.newspapersystems.com
15Sep15 wb initial version

Updated by Chus Rodriguez to generate iPray leaflets

"""

# A. check that the script is running from inside scribus
try:
	from scribus import *
except ImportError:
	print('This script only runs from within Scribus.')
	sys.exit(1)

# B. get the os module
try:
	import os
except ImportError:
	print('Could not import the os module.')
	sys.exit(1)

# Process imputs
def main(argv):
	pdf = scribus.PDFfile()

	if len(argv) != 5:
		print("Not the right number of arguments, the style should be: scribus... -py python_script.py pdf_destination_file pages_count tittle bleeding")
		return
	
	# destination file
	file_destination = argv[1]
	if not file_destination.endswith(".pdf"):
		print("The destination file {0} doesn't look like an pdf file".format(file_destination))
		return
	pdf.file = file_destination

	# num of pages
	num_pages = int(argv[2]) 
	if num_pages < 1:
		print("No pages to export in the pdf?")
		return
	pdf.pages = [i+1 for i in range(num_pages)]

	# get the leaflet tittle
	pdf.info = argv[3]

	# in the case of bleeding
	if argv[4] == 'True':
		pdf.cropMarks = 1
		pdf.bleedb = 3
		pdf.bleedt = 3
		pdf.bleedr = 3
		pdf.bleedl = 3
		pdf.markLength = 3
		pdf.markOffset = 1

	# pdf version
	pdf.version = 15
	
	# embed fonts
	fontEmbedding = 0

	pdf.save()

# start the script
if __name__ == '__main__':
	if haveDoc():
		main(sys.argv)
	else:
		print 'Error: You need to have a document open before you can run this script successfully.'