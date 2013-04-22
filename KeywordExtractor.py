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
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed

import csv

verbose = True

def getPdfs():
    url = 'http://www.morelab.deusto.es/'
    path_base = 'publications/'
    years = range(2006, 2014)
    if verbose:
        print "Downloading files"
    for y in years:
        path = path_base + str(y) + '/'
        d = os.path.dirname("./pdf/" + path)
        if not os.path.exists(d):
            os.makedirs(d)
        response = urllib2.urlopen(url+path).read()
        if verbose:
            print response
            print "\n************FILES**********\n"
        for filename in re.findall('"\S+.pdf"', response):
            filename = filename.replace('"', '')
            if verbose:
                print "Filename: " + filename
                print "URL: " + url + path + filename
            f = urllib2.urlopen(url + path + filename)
            data = f.read()
            with open("./pdf/" + path + filename, "wb") as code:
                code.write(data)
    
def get_pdf_content(path):
    laparams = LAParams()
    rsrc = PDFResourceManager()
    outfp = StringIO()
    try:
        #TODO: detect the encoding of the PDF        
        device = TextConverter(rsrc, outfp, codec="cp1252", laparams=laparams)
        process_pdf(rsrc, device, codecs.open(path))
    except (PDFSyntaxError, PDFTextExtractionNotAllowed):
        print "Error processing PDF file: " + path
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
            if verbose:
                print "Procesing" + file_path + name
            content = get_pdf_content(file_path + name)
            terms = get_terms_topia(content)           
            #paper_terms = [t[0] for t in terms if t[1] > 2 and not '\\x' in repr(t[0])]
            #still having problems with the encodings of the pdf file, the repr
            #is hopefully a temporal "workaround
            paper_terms = [t[0] for t in terms if t[1] > 2 and not is_bad(t[0]) and not '\\' in repr(t[0])]
            if verbose:
                print "  ->  Total terms: " + str(len(paper_terms))
            relations.append(paper_terms)
    
    if verbose:
        print "\n\n" + str(len(relations)) + " papers analized"
    return relations  

#curating the terms extracted with topia to delete some incorrect ones
def is_bad(term):
    invalid_terms = ['\\x', '.,', '(cid', '/', '/ i n', '/ f', '</', '><!--',
                       '),', '--></', '.:', '].', '[<', '[</', '</', '|k', '=0.6).',
                       'http ://www', '/ / www', '://drupal', '://www', '="http',
                       '="x', '(?', '),', '->', '2),', '(?', '),', '.,',
                       'T', 'P', 'V', 'U', 'l', 'J', 'F', 'L', 'D', 'W', 'S',
                       'b', 'm', 'w', 't', 'W m', 'n', 'r', 'r e', 'g', 'k',
                       '1.', '2.', '3.', '4.', '5.' '6.', '7.', '8.', '2.0-', '[4].',
                       '[1]', '[2]', '[3]', '[4]', '[5]', '[6]', '[7]', '[8]',
                       '[9]', '[10]', '[11]', '[12]', '[13]', '[14]', '[15]', 
                       '[16]', '[17]', '[18]', '[19]', '[24]', '[40]', 
                       'Fig', 'Figure', 'figure', 'e.g.', 'i.e.',                   
                       '-2006', '(2006).', '2011)',
                       'ontolo', 're', 'gy', 'http ://www http ://www DRAFT', 'et',
                       'al', '/her',
                       'Ordu', 'Garc']
                       
    if verbose:
        if term in invalid_terms:
            print "Invalid term: " + term
    return term in invalid_terms
   
def export_csv_undirected(relations):
    if verbose:
        print "\nExporting CSV"
    total_rels = 0
    with open('./data/termRelations.csv', 'wb') as file:
        #writer = csv.writer(csvfile, delimiter=';')
        for terms in relations:
            for term in terms:
                ind = terms.index(term)
                for i in range (ind+1, len(terms)):
                    file.write(term + ';' + terms[i] + '\n')
                    total_rels+=1
    if verbose:
        print "File exported, total relations: " + str(total_rels)
                    
if __name__ == "__main__":
#    content = get_pdf_content('./pdf/publications/2006/WebLabEWME2006.pdf')
#    print content
#    keywords = get_terms_topia(content)
#    print keywords
    rels = process_pdfs()
    export_csv_undirected(rels)