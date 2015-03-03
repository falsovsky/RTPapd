#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from bs4 import BeautifulSoup
import urllib2
import re
import unicodedata
import os
import string
import sys
import time

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
    match = re.search('wavrss(.+?)"', page.read())
    if match:
        if os.path.isfile(destfn):
            print "- Ja downloadada... a ignorar"
            return False
        print "- A sacar..."
        cmd = 'wget "http://rsspod.rtp.pt/podcasts/' + match.group(1) + '" -O "'+destfn+'"'
        os.system(cmd + "> /dev/null 2>&1")
        print "- Done"
        return True

if len(sys.argv) != 2:
    sys.exit("Correr com "+sys.argv[0]+" [progId]")

if sys.argv[1].isdigit():
    id = sys.argv[1]
else:
    sys.exit("progId tem de ser um numero")

exists = 0
c = 1
while True:
    print "--- Pagina " + str(c)
    url = "http://www.rtp.pt/play/bg_l_ep/?stamp=" + str(int(time.time())) + "&listDate=&listQuery=&listProgram=" + str(id) + "&listcategory=&listchannel=&listtype=recent&page=" + str(c) + "&type=all"
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read())

    if (soup.find('div') == None):
        sys.exit("ultima pagina")

    # apanha todos os items da pagina
    items = soup.findAll('div',{'class': 'lazy'})

    for item in items:
        if exists >= 5:
            sys.exit("A sair apos 5 falhas, ja devo ter tudo...")

        # url
        link = item.find('a')
        # data
        dt = item.find('span',{'class': 'small'}).contents[0].strip()
        dt = dt.replace(' ', '_')
        dt = dt.replace(',', '')

        # mudar para AAAA_MM_DD
        match = re.search(r"(\d+)_(\w+)_(\d+)", dt)
        if match:
           dt = match.group(3) + "_" + months[match.group(2)] + "_" + match.group(1)

        # parte ?
        pts = item.findAll('b',{'class': 'text-dark-gray'})
        try:
            pt = pts[1].contents[0]
            pt = pt.replace('...', '').strip()
            pt = pt.replace(' ', '_')
            pt = pt.replace('\n','')
        except IndexError:
            pt = ""

        print "-- " +  dt, pt

        title = removeDisallowedFilenameChars(dt + "-" + pt)
        if parseRTMP(link['href'],title,id) == False:
           exists = exists + 1

    c = c + 1

