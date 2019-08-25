### Link to the diferent functions to build each of the mediums

from ePub import build_epub
from ePub import build_mobi
from scribus import build_pdf
from appAndroid import build_app

build_functions = {
    "pdf" : build_pdf,
    "epub" : build_epub,
    "mobi" : build_mobi,
    "app" : build_app,
}