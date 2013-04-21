# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 12:29:52 2013

@author: aitor
"""

import re
import urllib2
#import pyPdf
from topia.termextract import extract

import os
from os import listdir
from os.path import isfile, join

import codecs
from cStringIO import StringIO
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.layout import LAParams

def getPdfs():
    url = 'http://www.morelab.deusto.es/'
    path_base = 'publications/'
    years = range(2006, 2014)
    
    for y in years:
        path = path_base + str(y) + '/'
        d = os.path.dirname("./pdf/" + path)
        if not os.path.exists(d):
            os.makedirs(d)
        
        response = urllib2.urlopen(url+path).read()
        
        print response
        
        print "\n************FILES**********\n"
        for filename in re.findall('"\S+.pdf"', response):
            filename = filename.replace('"', '')
            print filename
            print url + path + filename
            f = urllib2.urlopen(url + path + filename)
            data = f.read()
            with open("./pdf/" + path + filename, "wb") as code:
                code.write(data)
    

#def get_pdf_content(path):
#    content = ""
#    p = open(path, "rb")
#    pdf = pyPdf.PdfFileReader(p)
#    num_pages = pdf.getNumPages()
#    for i in range(0, num_pages):
#        content += pdf.getPage(i).extractText() + u"\n"
#    # content = " ".join(content.replace(u"\xa0", " ").strip().split())
#    new_content = u""
#    for c in content:
#        if '\\u' not in repr(c):
#            new_content += c
#    return new_content

def get_pdf_content(path):
    laparams = LAParams()
    rsrc = PDFResourceManager()
    outfp = StringIO()
    device = TextConverter(rsrc, outfp, codec="cp1252", laparams=laparams)
    process_pdf(rsrc, device, codecs.open(path))
    return outfp.getvalue()

def get_terms_topia(text):
    extractor = extract.TermExtractor()
    extractor.filter = extract.DefaultFilter(singleStrengthMinOccur=2)
    terms = sorted(extractor(text))
    return terms
    
def process_pdfs():
    years = range(2006, 2014)
    relations = []
    for y in years:   
        file_path = './pdf/publications/' + str(y) + '/'
        filenames = [ f for f in listdir(file_path) if isfile(join(file_path,f)) ]
        for name in filenames:
            content = get_pdf_content(file_path + name)
            terms = get_terms_topia(content)
            paper_terms = [t[0] for t in terms if t[1] > 2 and not '\\x' in repr(t[0])]
            print paper_terms
            relations.append(paper_terms)
    return relations      

if __name__ == "__main__":
#    content = get_pdf_content('./pdf/publications/2006/WebLabEWME2006.pdf')
#    print content
#    keywords = get_terms_topia(content)
#    print keywords
    rels = process_pdfs()
    print rels