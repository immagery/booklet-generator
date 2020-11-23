import os
import sys

print("Print running a script from a script", sys.argv[1])

import scribus



if len(sys.argv) < 2 :
    print("Not enough argumemnts")
else:
    if scribus.haveDoc():
        filename = sys.argv[1]
        pdf = scribus.PDFfile()
        pdf.file = filename + ".pdf"
        pdf.save()
    else :
        print("No file open")