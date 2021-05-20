#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import string
import requests
from bs4 import BeautifulSoup


def fix_filename(filename):
    filename = filename.replace(' ', '_')
    safechars = bytearray(('_-.()' + string.digits + string.ascii_letters).encode())
    allchars = bytearray(range(0x100))
    deletechars = bytearray(set(allchars) - set(safechars))
    return filename.encode('ascii', 'ignore').translate(None, deletechars).decode()

def parse_episodes(progId):
    page = 1
    while True:
        url = "https://www.rtp.pt/play/bg_l_ep/?listProgram={}&page={}".format(progId, page)
        print("Scraping Page {} ({})".format(page, url))
        response = requests.get(
            url,
            headers={
                'User-agent': 'Mozilla/5.0',
                'Cookie': 'rtp_cookie_parental=0; rtp_privacy=666; rtp_cookie_privacy=permit 1,2,3,4; googlepersonalization=1; _recid='
                }
        )
        soup = BeautifulSoup(response.content, "html.parser")

        if soup.find('article') is None:
            sys.exit("No more pages.")

        for article in soup.find_all('article'):
            url = article.find('a')['href']
            episode_date = article.find('span', {'class': 'episode-date'})
            episode_title = article.find('h4', {'class': 'episode-title'})
            yield {
                'url': "https://rtp.pt{}".format(url),
                'filename': fix_filename(
                    "{}-{}.mp3".format(
                        episode_date.text.strip(),
                        episode_title.text.strip() if episode_title else ''
                    )
                )
            }
        page += 1

def download_episode(episode, local_file):
    response = requests.get(
        episode['url'],
        headers={
            'User-agent': 'Mozilla/5.0',
            'Cookie': 'rtp_cookie_parental=0; rtp_privacy=666; rtp_cookie_privacy=permit 1,2,3,4; googlepersonalization=1; _recid='
            }
    )
    file_url = re.search(r"f = \"(.*?)\"", response.text)
    if file_url:
        cmd = "wget \"{}\" -O \"{}\" > /dev/null 2>&1".format(
            file_url.group(1),
            local_file
        )
        print("Downloading {} ...".format(local_file))
        os.system(cmd)
        print("Done.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Run with {} [progId]".format(sys.argv[0]))

    if sys.argv[1].isdigit():
        progId = sys.argv[1]
    else:
        sys.exit("progId must be numeric")

    script_path = os.path.dirname(os.path.realpath(__file__))
    directory = "{}/{}".format(script_path, progId)
    if os.path.isdir(directory) is False:
        os.makedirs(directory)

    failed = 0
    for episode in parse_episodes(progId):
        if failed >= 5:
            sys.exit("Already have 5 files...")
        local_file = "{}/{}".format(
            directory,
            episode['filename']
        )
        if os.path.isfile(local_file):
            failed += 1
            continue
        download_episode(episode, local_file)
