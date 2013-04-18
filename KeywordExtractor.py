# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 12:29:52 2013

@author: aitor
"""

import re
import urllib2
import os
import pyPdf
from topia.termextract import extract

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
    

def get_pdf_content(path):
    content = ""
    p = file(path, "rb")
    pdf = pyPdf.PdfFileReader(p)
    num_pages = pdf.getNumPages()
    for i in range(0, num_pages):
        content += pdf.getPage(i).extractText() + "\n"
    content = " ".join(content.replace(u"\xa0", " ").strip().split())    
    return content.encode('UTF-8')

def get_terms_topia(text):
    extractor = extract.TermExtractor()
    terms = sorted(extractor(text))
    return terms
        

if __name__ == "__main__":
    content = get_pdf_content('./pdf/publications/2006/WebLabEWME2006.pdf')
    keywords = get_terms_topia(content)
    print keywords
    
