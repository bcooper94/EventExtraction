# Author: Joey Wilson

import sys
import re
import json
import time
import requests
import bs4

ROOT_URL = 'http://www.wikicfp.com/cfp/allcat'
CATEGORY_URL = 'http://www.wikicfp.com/cfp/call?conference={}&page={}' # called with .format(<page number>)
PAGE_URL = 'http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid={}&copyownerid={}' # called with .format(<eventid>, <copyownerid>)
DATABASE = []
EXISTS = {}

def scrape_page(html):
   global DATABASE, EXISTS
  
   data = {
      'name': None,
      'start': None,
      'stop': None,
      'submission deadline': None,
      'notification due': None,
      'final version due': None,
      'link': None,
      'html': None,
      'categories': None
   }
 
   soup = bs4.BeautifulSoup(html, 'html.parser')

   name = soup.find('h2').get_text().strip()
   data['name'] = name

   # check for duplicates
   if name in EXISTS:
      return
  
   tables = soup.find_all('table')

   for r in tables[8].find_all('tr'):
      key = r.find('th').get_text().lower().strip()
      value = r.find('td').get_text().strip()
      if key == 'when':
         when = value.split('-')
         if len(when) == 2:
            data['start'] = when[0] 
            data['stop'] = when[1]
      else:
         if 'N/A' in value:
            data[key] = None
         else:
            data[key] = value

   data['categories'] = []
   for r in tables[9].find_all('a')[1:]:
      data['categories'].append(r.get_text().strip())

   m = re.search('Link: <a href="([^"]+)"', html)
   if m == None: # if there is no link, just throw it out
      return 

   data['link'] = m.group(1)
   r = None
   data['html'] = None
   try:
      r = requests.get(data['link'], timeout=5)
   except:
      print('Error getting {}: {}'.format(data['link'], sys.exc_info()))
   if r and r.status_code == 200 and r.headers['content-type'] != 'application/pdf':
      print(data['link'], r.status_code)
      data['html'] = r.text

   EXISTS[name] = 1
   DATABASE.append(data)

def scrape_page_list(html):
   global PAGE_URL
   for l in re.findall('event\.showcfp\?eventid=([0-9]+)&amp;copyownerid=([0-9]+)', html):
      r = requests.get(PAGE_URL.format(l[0], l[1]), timeout=5)
      scrape_page(r.text)

def scrape_category(category):
   global CATEGORY_URL
   print('Category: {}'.format(category))
   for i in range(1, 20): # change to range(1,20) to get all of the pages
      print('PAGE: {}'.format(i))
      r = requests.get(CATEGORY_URL.format(category, i), timeout=5)
      scrape_page_list(r.text)

def scrape():
   global ROOT_URL
   r = requests.get(ROOT_URL, timeout=5)
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
