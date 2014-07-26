RTPapd
======

RTP audio podcasts downloader

Requirements:
- Python
- Beautiful Soup - http://www.crummy.com/software/BeautifulSoup/
- wget

Features:
- Downloads the full podcast archive
- Can be run in cron to download the latest ones
- After 5 "already downloaded" files it exits
- Uses a different directory per progId

Instructions:
- Extract the "bs4" directory from the Beautiful Soup package to the directory of the script.
- Run the script with an argument that is the progId to download

Example:
- The URL for the "Costa a Costa" program is http://www.rtp.pt/play/p1085/costa-a-costa so our progId is 1085.
- To download it just do:
```
./rtp.py 1085
```
