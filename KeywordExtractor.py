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
                print "Processing" + file_path + name
            content = get_pdf_content(file_path + name)
            terms = get_terms_topia(content)           
            #paper_terms = [t[0] for t in terms if t[1] > 2 and not '\\x' in repr(t[0])]
            #still having problems with the encodings of the pdf file, the repr
            #is hopefully a temporal "workaround
            paper_terms = [t[0].strip() for t in terms if t[1] > 4 and not is_bad(t[0].strip()) and not '\\' in repr(t[0])]
            if verbose:
                print "  ->  Total terms: " + str(len(paper_terms))
            relations.append(paper_terms)
    
    if verbose:
        print "\n\n" + str(len(relations)) + " papers analized"
    return relations  

#SUSPICIOUS = []

#curating the terms extracted with topia to delete some incorrect ones
def is_bad(term):
    bad = False
    invalid_terms = ['\\x', '.,', '(cid', '/', '/ i n', '/ f', '</', '><!--',
                       '),', '--></', '.:', '].', '[<', '[</', '</', '|k', '=0.6).',
                       'http ://www', '/ / www', '://drupal', '://www', '="http',
                       '="x', '(?', '),', '->', '2),', '(?', '),', '.,', '(%)', '(1',
                       '|', ',i', '(c', ',5',
                       'W m', 'r e', '2.0-',
                       'Fig', 'Figure', 'figure', 'e.g.', 'i.e.', 'e.g', 'e.g .,',
                       'i.e', 'i.e.,', 'i.e .,',
                       '-2006', '(2006).', '2011)',
                       'ontolo', 're', 'gy', 'http ://www http ://www DRAFT', 'et',
                       'al', '/her', 'Elect', 'tion', '2let', 'st',
                       '08-09', '10-11',
                       'Ordu', 'Garc', 'Universidades 24, 48007, Bilbao', 'tion',
                       'del.icio.u', 'del.icio.u', 'user \x92s', '\xf3pez', '2Object',
                       'EMI 2Object', 'EMI 2Objects', 'EMI 2let', 'EMI 2let Player',
                       'EMI 2let Server', 'EMI 2lets', 'EMI 2lets platform', 'L \xf3pez',
                       '\xe1zquez', '\xf1a', '\xf3pez', 'Web 2.0-', '</ action', 
                       '</ argumentList', '>actionName', 'name >actionName',
                       '2.Control', '2Button', '2Peer', 'EMI 2Peer', 'EMI 2Peers',
                       'EMI 2let', 'EMI 2let Player', 'EMI 2let Server', 'EMI 2lets',
                       'EMI 2lets platform', '\xf3pez', '\xf1a', '@eside', '\xeda',
                       '="urn', '2Object', '2Protocol', 'EMI 2Object', 'EMI 2Objects',
                       'EMI 2let', 'EMI 2let Player', 'EMI 2let Server', 'EMI 2let server-side',
                       'EMI 2lets', 'EMI 2lets platform', '\xf1a', '\xf3pez', '\xe1ctica',
                       '\xf1o', '1, MARCH 2005 DRAFT', 'Diego L \xb4 opez', 'Ipi \x98',
                       '/cm', '\xe6a', '09, 2006 Florianopolis', '\xe1ndez', '\xeda',
                       '\xf1a', 'Web 2.0 technologies', '\x92t', ':name', ':type',
                       '://deusto', ':type', 'http ://deusto', 'Web 2.0-', '\x98na',
                       'estaci \xf3n base', 'informaci \xf3n', 'interacci \xf3n',
                       '\xe1mbrica', '\xe1n', '\xe9n', '\xe9tica', '\xe9tico',
                       '\xeda', '\xedda', '\xf1o', '\xf3lo', '\xf3n', '\xfan','2onto',
                       'WWW 2006, Edinburgh', 'del.icio.u', 'folk 2onto',
                       '1-1569228491-2409\xa9SoftCOM', '(URI', '(URI space', 
                       '<ITriple', ':Ciudad', 'user \x92s', 'ElderCare \x92s',
                       '\x1berent', ':Pablo', ':Person', ':SecretClas', ':fullName',
                       ':name', 'b 1', 'b 1 injection :name', 'injection :Pablo injection :fullName',
                       'injection :Person', 'injection :SecretClass', 'name 1',
                       'p 1', 'p 1 injection :fullName', 'p 2', '/IEC', '>test',
                       'aplicaci \xf3n', 'evaluaci \xf3n', '\xd3N', '\xe1lculo',
                       '\xe1lisi', '\xe1ndar', '\xe9n', '\xe9trica', '\xeda',
                       '\xedculo', '\xf3dulo', '\xf3n', '\xf3vil', '\xf3vile',
                       '/IEC', '\xe1n', '\xeda', '\xedgrafo', '\xf1o', '\xf3dulo',
                       '\xf3n', '\xf1a', '\xf3pez', '\xf3pez', 'CAIS 2011', "EMS ',",
                       'extracci \xf3n', 'precisi \xf3n', 't \xe9rminos', '\x92,\x92fem',
                       '\x92,\x92sg', '\xe1gina', '\xe1lisi', '\xe1tica', '\xe9dico',
                       '\xe9rmino', '\xe9tera', '\xe9todo', '\xeda', '\xedan', '\xeddo',
                       '\xf3n', '\xf3nica', '\xfamero', '\xfc\xedstica', '(w', 'room 0.11',
                       '(sp', '://nodeuri', 'http ://nodeuri', '\x98na', '\xb4omez',
                       '\x98na', '\xb4omez', '://nodeuri', 'FoxG 20', '\xf3pez', '/IEC',
                       '?How', '\xf3n', "'2011ISBN", '\x92,\x91fem', '\x92,\x91sg', '\xb4a',
                       '\xb4o', '\xb4on', '\xb4onica', '/10/$25.00 \xa92011 IEEE April 4',
                       '6, 2011, Amman', 'Jordan IEEE EDUCON Education Engineering 2011 \x96 Learning Environments',
                       '\xf1a', '/IEEE', '15, 2011, Rapid City', '@ieec', 
                       'SD 978-1-61284-469-5/11/$26.00 \xa92011 IEEE 41 st ASEE /IEEE Frontiers',
                       '/IEEE', '15, 2011, Rapid City', '@deusto', 
                       'SD 978-1-61284-469-5/11/$26.00 \xa92011 IEEE 41 st ASEE /IEEE Frontiers',
                       '\xeda', '\xf1a', '2009-2010 course', ':1829)(cid', ':1832)(cid',
                       ':1842)(cid', ':1865)(cid', ':4666)(cid', 'cid :1829)(cid',
                       'cid :1845)', 'cid :1865)(cid', 'cid :3397) 0.95', 'cid :3400)',
                       'cid :3404)', 'cid :4667)', '://nodeuri', 'FoxG 20', '+Jena',
                       'W 3C', 'n p 0', 'p 0', 'S \xb3OiA', '\xb3OiA', '\xf3pez',
                       ':10.1016/j', ':10.3758/BF', 'J .,', 'R .,', 'S .,', '\xe1rcena',
                       '\xeda', '\xf1o', '/IP', '\xb4opez', '/XML', 'gesti \xf3n', 
                       'gesti \xf3n del contexto', 'informaci \xf3n', '\xe1n',
                       '\xe1ntica', '\xe1ntico', '\xe9todo', '\xeda', '\xedncrona',
                       '\xedstica', '\xf1adir', '\xf1o', '\xf3dulo', '\xf3n', '\xf3vile',
                       '\xfan', 'K authS ,A', 'K encS ,A', '_time', '3 DU Blocks', 
                       '3 DU Blocks Music', '3 DU Blocks library', '3 DU Blocks',
                       '3 DU Blocks Music', '3 DU Blocks library']
    
    if len(re.findall('^,[A-Za-z]*',term)) > 0:
        bad  = True   
    elif len(re.findall('^,\d',term)) > 0:
        bad  = True         
    elif len(re.findall('^\[\d+\]',term)) > 0:
        bad  = True 
    elif len(re.findall('^\d+.$',term)) > 0:
        bad  = True
    elif len(re.findall('^[A-Z]$',term)) > 0:
        bad = True    
    elif len(re.findall('^[a-z]$',term)) > 0:
        bad = True 
    elif len(re.findall('^\d+$',term)) > 0:
        bad = True   
    elif len(re.findall('^\d+.\d+$',term)) > 0:
        bad = True    
    elif len(re.findall('^[^A-Za-z]*$',term)) > 0:
        bad = True
    elif term in invalid_terms:
        bad = True
#    elif len(re.findall('^[A-Za-z -]*$',term)) == 0:
#        print "Sospechoso:", term, repr(term)
#        SUSPICIOUS.append(term)
 
    return bad
   
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
    import pprint
#    pprint.pprint(SUSPICIOUS)