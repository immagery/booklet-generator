iPray booklet generator
=======================

Intallation and getting ready
-----------------------------

This is a Python based app to generate iPray booklets

for development I'm using several python packages to make our life easier:

<p>pip install Jinja2
<p>pip install gspread
<p>pip install --upgrade oauth2client
<p>pip install PyOpenSSL
<p>pip install git+https://github.com/jachinlin/kindle_maker.git

And spreadsheets as a database for all the texts. Here the instructions I have followed to get my ready the system to read that database:

https://gspread.readthedocs.io/en/latest/oauth2.html

In order to access the database you need the credentials, created through:

https://console.developers.google.com/apis


Things to have into account when running it
-------------------------------------------

* The database has to be in a google spreadsheet shared with the right address to access through the API

Running the build
-----------------

python .\src\build_iPray.py D:\dev\booklet-generator\data\ 2023

You will need scribus 1.5.7+ to open the result and generate the final booklet pdf
You need to install the keepcalm font to edit the cover