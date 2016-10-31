# Author: Joey Wilson

import requests
import re
import time

ROOT_URL = 'http://www.wikicfp.com/cfp/call?conference=computer%20science&page={}' # called with .format(<page number>)
SINGLE_URL = 'http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid={}&copyownerid={}' # called with .format(<eventid>, <copyownerid>)

def scrape_page(html):
   m = re.search('Link: <a href="([^"]+)"', html)
   print 'Link: {}'.format(m.group(1))
   m = re.search('<th>When</th>\s*<td align="center">([^<]+)</td>', html)
   print 'When: {}'.format(m.group(1).strip())
   m = re.search('<th>Where</th>\s*<td align="center">([^<]+)</td>', html)
   print 'Where: {}'.format(m.group(1).strip())

def scrape_page_list(html):
   m = re.findall('event\.showcfp\?eventid=([0-9]+)&amp;copyownerid=([0-9]+)', html)
   for l in m:
      r = requests.get(SINGLE_URL.format(l[0], l[1]))
      time.sleep(1)
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
   scrape()

if __name__ == '__main__':
   main()
