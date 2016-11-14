# Author: Joey Wilson

import requests
import re
import json
import time
import bs4

ROOT_URL = 'http://www.wikicfp.com/cfp/allcat'
CATEGORY_URL = 'http://www.wikicfp.com/cfp/call?conference={}&page={}' # called with .format(<page number>)
PAGE_URL = 'http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid={}&copyownerid={}' # called with .format(<eventid>, <copyownerid>)
DATABASE = []

def scrape_page(html):
   global DATABASE
   data = {}
   m = re.search('<span property="v:description">([^<]+)</span>', html)
   if m and m.group(1):
      data['name'] = m.group(1).strip()
   m = re.search('Link: <a href="([^"]+)"', html)
   if m and m.group(1):
      data['link'] = m.group(1).strip()
   m = re.search('<th>When</th>\s*<td align="center">([^<]+)</td>', html)
   if m and m.group(1):
      data['when'] = m.group(1).strip()
   m = re.search('<th>Where</th>\s*<td align="center">([^<]+)</td>', html)
   if m and m.group(1):
      data['where'] = m.group(1).strip()
   data['html'] = '' 
   print(data['link'])
   if data['link']:
      r = requests.get(data['link'])
      print(r.status_code)
      if r.status_code == 200:
         data['html'] = r.text  
   DATABASE.append(data)

def scrape_page_list(html):
   global PAGE_URL
   for l in re.findall('event\.showcfp\?eventid=([0-9]+)&amp;copyownerid=([0-9]+)', html):
      r = requests.get(PAGE_URL.format(l[0], l[1]))
      scrape_page(r.text)

def scrape_category(category):
   global CATEGORY_URL
   print('Category: {}'.format(category))
   for i in range(1, 2): # change to range(1,20) to get all of the pages
      r = requests.get(CATEGORY_URL.format(category, i))
      scrape_page_list(r.text)

def scrape():
   r = requests.get(ROOT_URL)
   soup = bs4.BeautifulSoup(r.text, 'html.parser')
   categories = map(lambda link: link.get_text(), soup.find_all('table')[3].find_all('a'))
   for i in range(0, 1): # chage to for c in categories to get all the categories
      scrape_category(categories[i])

def main():
   global DATABASE
   scrape()
   f = open('output.json', 'w')
   f.write(json.dumps(DATABASE, indent=3, separators=(',', ': ')))
   f.close()

if __name__ == '__main__':
   main()
