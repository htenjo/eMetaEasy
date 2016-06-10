#!/usr/bin/env python
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from PyPDF2 import PdfFileReader, PdfFileMerger

from slugify import Slugify
import os
import isbnlib


# returns the directory path to process given by the user
def get_directory_name():
    print "-> Get Directory Path..."
    directory_path = raw_input("Directory path: ")
    return directory_path;


# returns a list of names (with extension, without full path) of all files
# in folder path
def list_files(directory_path):
    """
    :param directory_path: Path of the directory to search pdf e-books
    :rtype: File[]
    """
    print "-> Listing files..."
    files = []

    for name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, name)
        is_file = os.path.isfile(file_path)
        is_pdf = file_path.endswith(FILE_DEFAULT_EXTENSION)

        if is_file and is_pdf:
            files.append(file_path)
    return files


# Returns the ISBN code in formatted way
def get_default_isbn(isbn_list):
    for isbn in isbn_list:
        if isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn):
            return isbnlib.mask(isbn)

    return ""


# /Users/htenjo/eBooks
def get_isbn_from_file(file_name, max_pdf_pages=0):
    print "-> Getting ISBN from PDF files..."

    # PDFMiner boilerplate
    rsrcmgr = PDFResourceManager()
    sio = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Extract text
    fp = file(file_name, 'rb')
    num_pages = 1

    for page in PDFPage.get_pages(fp, maxpages=max_pdf_pages):
        interpreter.process_page(page)
        num_pages += 1

    print "Pages processed = " + str(num_pages)
    fp.close()
    # Get text from StringIO
    text = sio.getvalue()
    # Cleanup
    device.close()
    sio.close()
    default_isbn = get_default_isbn(isbnlib.get_isbnlike(text))
    return default_isbn


# Assign the attribute metadata names required by Calibre and some other readers
def clean_metatada(meta):
    filled_metadata = {}

    for meta_key in meta:
        if meta[meta_key] != "":
            if meta_key == AUTHOR_PROPERTY_NAME:
                filled_metadata[AUTHOR_META_NAME] = ",".join(meta[meta_key])
            elif meta_key.startswith(ISBN_PROPERTY_NAME):
                filled_metadata[ISBN_META_NAME] = meta[meta_key]
            elif meta_key.startswith(TITLE_PROPERTY_NAME):
                filled_metadata[TITLE_META_NAME] = meta[meta_key]

    return filled_metadata


# Add the metadata fields directly in the pdf file and in the file name
def add_metadata(file_name, metadata, directory_name):
    title = my_slugify(metadata[TITLE_META_NAME]);
    authors = my_slugify(metadata[AUTHOR_META_NAME]);
    isbn = my_slugify(metadata[ISBN_META_NAME]);
    new_file_name = directory_name + "processed/" + title
    processed_file_name = directory_name + DEFAULT_OLD_FOLDER + title + FILE_DEFAULT_EXTENSION

    print "-> Adding metadata to file... %s", new_file_name
    merger = PdfFileMerger()
    print "ADD METADATA 0"
    print "::: ", file_name
    merger.merge(position=0, fileobj=PdfFileReader(file_name, "rb"))

    print "ADD METADATA 1"
    merger.addMetadata(metadata)
    print "ADD METADATA 2"
    with open(new_file_name + DASH_SEPARATOR + authors + DASH_SEPARATOR + isbn
                      + FILE_DEFAULT_EXTENSION, 'wb') as pdf_file_reference_updated:
        merger.write(pdf_file_reference_updated)
    print "ADD METADATA 3"
    os.rename(file_name, processed_file_name);
    print "File processed OK"


# Gets the new path where old files going to be moved
def get_new_file_name_from_old_path(file_name):
    file_name = str(file_name)
    last_slash_index = file_name.rfind("/")
    dir_path = file_name[:last_slash_index+1]
    new_file_name = file_name[last_slash_index+1:]
    new_file_name = my_slugify(new_file_name)
    new_file_name = dir_path + DEFAULT_PENDING_FOLDER + new_file_name
    return new_file_name


# Main function
def set_ebook_metadata():
    print "::: PDF Metadata running... "
    # directory_name = get_directory_name()
    directory_name = "/Users/htenjo/eBooks/"
    files = list_files(directory_name)

    for file_name in files:
        try:
            print "::: Processing file %s ..." % file_name
            isbn = get_isbn_from_file(file_name)
            print "ISBN OK"
            metadata = isbnlib.meta(isbn)
            print "METADATA OK"

            if metadata is None:
                os.rename(file_name, get_new_file_name_from_old_path(file_name));
                continue

            metadata = clean_metatada(metadata)
            print metadata
            print "METADATA CLEANED"

            if metadata.has_key(TITLE_META_NAME) and \
                    metadata.has_key(AUTHOR_META_NAME) and metadata.has_key(ISBN_META_NAME):
                add_metadata(file_name, metadata, directory_name)
            else:
                os.rename(file_name, get_new_file_name_from_old_path(file_name))
        except Exception as err:
            os.rename(file_name, get_new_file_name_from_old_path(file_name))
            print "ERROR: File with errors ", file_name, err.__str__()


TITLE_PROPERTY_NAME = "Title"
TITLE_META_NAME = "/Title"
AUTHOR_PROPERTY_NAME = "Authors"
AUTHOR_META_NAME = "/Author"
ISBN_PROPERTY_NAME = "ISBN"
ISBN_META_NAME = "/ISBN"
FILE_DEFAULT_EXTENSION = ".pdf"
DASH_SEPARATOR = " -- "
DEFAULT_SEPARATOR = " "
DEFAULT_OLD_FOLDER = "old/"
DEFAULT_PENDING_FOLDER = "Waiting4ManualCheck/"

my_slugify = Slugify()
my_slugify.separator = DEFAULT_SEPARATOR
my_slugify.safe_chars = '-.'

set_ebook_metadata()


