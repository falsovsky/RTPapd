#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import re
import unicodedata
import os
import string

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


validFilenameChars = "-_. %s%s" % (string.ascii_letters, string.digits)

def removeDisallowedFilenameChars(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def parseRTMP(url,dt):
    url = 'http://www.rtp.pt' + url
    page = urllib2.urlopen(url)
    match = re.search('"file": "(.*?)","application": "(.*?)","streamer": "(.*?)"', page.read(), re.MULTILINE)
    if match:
        fn = match.group(1).split('/')[5].replace('.mp3', '.flv')
        cmd = 'rtmpdump -r "rtmp://' + match.group(3) + '/' + match.group(2) + '" -y "mp3:' + match.group(1) + '" -o "'+ dt + '.flv"'

        #print cmd
        if os.path.isfile(dt+'.mp3'):
            print "- Ja downloadada... a ignorar"
            return

        print "- A sacar..."
        os.system(cmd + "> /dev/null 2>&1")
        print "- A extrair mp3 do flv..."
        os.system('ffmpeg -i "' + dt + '.flv" -acodec copy "'+dt+'.mp3" > /dev/null 2>&1')
        os.remove(dt + '.flv')
        print "- Done"

id = "1085"

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
        parseRTMP(link['href'],title)



