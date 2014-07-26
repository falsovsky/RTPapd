#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import re
import unicodedata
import os
import string
import sys

months = {
        'Jan': '01',
        'Fev': '02',
        'Mar': '03',
        'Abr': '04',
        'Mai': '05',
        'Jun': '06',
        'Jul': '07',
        'Ago': '08',
        'Set': '09',
        'Out': '10',
        'Nov': '11',
        'Dez': '12'
        }

scriptpath = os.path.dirname(os.path.realpath(__file__))
validFilenameChars = "-_. %s%s" % (string.ascii_letters, string.digits)

def removeDisallowedFilenameChars(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def parseRTMP(url,title,progId):
    url = 'http://www.rtp.pt' + url
    programpath = scriptpath+"/"+progId
    if os.path.isdir(programpath) == False:
            os.makedirs(programpath)
    destfn = programpath+"/"+title+'.mp3'
    page = urllib2.urlopen(url)
    match = re.search('"file": ".*?//(.*?)"', page.read(), re.MULTILINE)
    if match:
        if os.path.isfile(destfn):
            print "- Ja downloadada... a ignorar"
            return
        print "- A sacar..."
        cmd = 'wget "http://rsspod.rtp.pt/podcasts/' + match.group(1) + '" -O "'+destfn+'"'
        os.system(cmd + "> /dev/null 2>&1")
        print "- Done"

if len(sys.argv) != 2:
    sys.exit("Run with "+sys.argv[0]+" [progId]")

if sys.argv[1].isdigit():
    id = sys.argv[1]
else:
    sys.exit("progId must be a number")

# apanhar o numero total de paginas
url = "http://www.rtp.pt/play/browseprog/"+id+"/1/true"
page = urllib2.urlopen(url)
match = re.search(r'<a title="Fim.*?,page:(\d+)\}', page.read(), re.MULTILINE)
if match:
    totalpages = match.group(1)
else:
    exit

for c in range(1,int(totalpages)):
    print "--- Pagina " + str(c)
    url = "http://www.rtp.pt/play/browseprog/"+id+"/"+str(c)+"/"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())

    # apanha todos os items da pagina
    items = soup.findAll('div',{'class': 'Elemento'})

    for item in items:
        # url
        link = item.find('a')
        # data
        dt = item.find('b').contents[0].strip()
        dt = dt.replace(' ', '_')

        # mudar para AAAA_MM_DD
        match = re.search(r"(\d+)_(\w+)_(\d+)", dt)
        if match:
                dt = match.group(3) + "_" + months[match.group(2)] + "_" + match.group(1)

        # parte ?
        pt = item.find('p').contents[0].strip()
        pt = pt.replace(' ', '_')

        print "-- " +  dt, pt

        title = removeDisallowedFilenameChars(dt + "-" + pt)
        parseRTMP(link['href'],title,id)



