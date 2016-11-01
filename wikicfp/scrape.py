# Author: Joey Wilson

import requests
import re
import time

ROOT_URL = 'http://www.wikicfp.com/cfp/call?conference=computer%20science&page={}' # called with .format(<page number>)
SINGLE_URL = 'http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid={}&copyownerid={}' # called with .format(<eventid>, <copyownerid>)

OUT_FILE = None

def scrape_page(html):
   global OUT_FILE
   f = OUT_FILE
   m = re.search('Link: <a href="([^"]+)"', html)
   f.write('Link: {}\n'.format(m.group(1)))
   m = re.search('<th>When</th>\s*<td align="center">([^<]+)</td>', html)
   f.write('When: {}\n'.format(m.group(1).strip()))
   m = re.search('<th>Where</th>\s*<td align="center">([^<]+)</td>', html)
   f.write('Where: {}\n\n'.format(m.group(1).strip()))

def scrape_page_list(html):
   m = re.findall('event\.showcfp\?eventid=([0-9]+)&amp;copyownerid=([0-9]+)', html)
   for l in m:
      print 'Working ...'
      r = requests.get(SINGLE_URL.format(l[0], l[1]))
      scrape_page(r.text)

def scrape():
   global ROOT_URL, SINGLE_URL
   r = requests.get(ROOT_URL.format(1))
   html = r.text
   m = re.search('Total of ([0-9]+) CFPs in ([0-9]+) pages', html)
   num_cfp = m.group(1)
   num_pages = m.group(2)
   print 'Number of CFPs: {}'.format(num_cfp)
   print 'Number of pages: {}'.format(num_pages)
   #for i in range(1, num+pages)
   #   r = requests.get(ROOT_URL.format(i))
   #   scrape_page_list(html)
   scrape_page_list(html)

def main():
   global OUT_FILE
   OUT_FILE = open('output.txt', 'w')
   scrape()
   OUT_FILE.close()

if __name__ == '__main__':
   main()
