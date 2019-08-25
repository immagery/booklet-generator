#!python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys
import codecs
import glob
import json
import re

INPUT_ENCODING = "utf-8-sig"
OUTPUT_ENCODING = "utf-8"

def parse_text(text):
    """Scan the input file one line at a time, looking for a keyword
    at the start of the line which will be one word in capital letters
    followed by a colon. This introduces a text suite, possibly over several
    lines which lasts until the next keyword or the end of the text.

    Lines which start with a hash sign (#) are treated as comments
    and are ignored.
    """
    keyword_matcher = re.compile(r"([A-Z]+)\:\s*(.*)", flags=re.UNICODE)

    #
    # The text consists of a number of blocks, introduced by a keyword
    # and containing one or more paragraphs. This parser yields the keyword
    # and a list of the paragraphs. For some keywords, this list will always
    # contain exactly one string.
    #
    keyword = None
    paragraphs = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        match = keyword_matcher.match(line)
        if match:
            if keyword:
                yield keyword, paragraphs
            keyword, text = match.groups()
            paragraphs = [text.strip()]
        else:
            paragraphs.append(line.strip())

    #
    # If we fall out of the loop with a keyword & text
    # remaining (which is the most likely case) then yield
    # both
    #
    if keyword and paragraphs:
        yield keyword, paragraphs

def process_title(texts):
    """Take a title with an optional subtitle in brackets and
    yield both as TITLE / SUBTITLE
    """
    text = " ".join(texts)
    #
    # Match as many non-left-bracket characters as possible
    # Then, optionally, match text in brackets
    #
    title, subtitle = re.match(r"([^(]+)\s*(?:\(([^)]+)\))?", text, flags=re.UNICODE).groups()
    yield "TITLE", title
    yield "SUBTITLE", subtitle

def process_gospel(texts):
    """Take a gospel quote prefixed by a chapter-and-verse reference.
    NB The chapter-and-verse must be on the same line as the "GOSPEL:"
    tag but the quote must be on a new line -- this makes it easier
    (read: possible) to parse the messy citations you can get.
    """
    text = "%s\n%s" % (texts[0], " ".join(texts[1:]))
    citation, gospel = re.match(r"([^\n]+)\n(.*)", text, flags=re.UNICODE).groups()
    yield "CITATION", citation
    yield "GOSPEL", gospel

style_markers = {
    "_" : "italic",
    "*" : "bold",
    "@" : "boldItalic"
}
def process_paragraph(paragraph):
    """Generate tuples of (style, text) where the default
    style is normal, and an underscore introduces an italic style
    and an asterisk introduces a bold style.
    """
    state = "normal"
    text = ""
    for c in paragraph:
        for marker, style in style_markers.items():
            if c == marker:
                if text:
                    yield state, text
                    text = ""
                state = "normal" if state == style else style
                break
        else:
            text += c

    if text:
        yield state, text

def process_comments(texts):
    """The comments field is processed specially so that blocks which are
    tagged as italic or bold (surrounded by _ or *) can be broken out into
    separate blocks and tagged as such.
    """
    comments = []
    for paragraph in texts:
        comment = list(process_paragraph(paragraph))
        if comment:
            comments.append(comment)
    yield "COMMENTS", comments


def break_and_process_comments(text):
    paragraphs = []
    for line in text.splitlines():
        comment = list(process_paragraph(line.strip()))
        if comment:
            paragraphs.append(comment)
    return paragraphs

#
# Each processor takes a list of paragraphs and yields
# tuples of keyword, paragraphs. This allows a single source
# line to become more than one keyword / text. eg a title
# which looks like this:
#   TITLE: This is a title (With a subtitle)
# can yield:
#  TITLE, This is a title
#  SUBTITLE, With a subtitle
#
PROCESSORS = {
    "TITLE" : process_title,
    "GOSPEL" : process_gospel,
    "COMMENTS" : process_comments
}

def process_one_file(filepath):
    items = {}
    with codecs.open(filepath, encoding=INPUT_ENCODING) as f:
        for keyword, paragraphs in parse_text(str(f.read())):
            items.update(PROCESSORS[keyword](paragraphs))
    return items

def process_one_folder(dirpath, include_subfolders=True):
    text = {}
    if include_subfolders:
        filepaths = []
        for dirname, dirnames, filenames in os.walk(dirpath):
            for filename in filenames:
                if filename.endswith(".txt"):
                    filepaths.append(os.path.join(dirname, filename))
    else:
        filepaths = glob.glob(os.path.join(dirpath, "*.txt"))
        
    for filepath in sorted(filepaths):
        print(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        text[name] = dict(process_one_file(filepath))
    return text

def process_one_thing(path):
    if os.path.isdir(path):
        return process_one_folder(path)
    else:
        print(path)
        return process_one_file(path)

if __name__ == '__main__':
    import pprint
    with codecs.open("parse.txt", "wb", encoding=INPUT_ENCODING) as f:
        f.write("# -*- coding: utf-8 -*-\n")
        pprint.pprint(process_one_thing(*sys.argv[1:]), f)
        #~ json.dump(process_one_folder(*sys.argv[1:]), f)
