from bs4 import BeautifulSoup
from subprocess import call
import re


def getDynamicPage(url: str):
    fileLoc = 'html/'
    phantom = call(['phantomjs', 'crawler.js', url, fileLoc])
    if phantom != 0:
        raise ConnectionError('Phantom failed to retrieve' + url)

    page = None

    return page


def extractUrls(page: BeautifulSoup, domain):
    pattern = re.compile('(https?://){}'.format(domain))
    links = page.find_all('a')
    tables = page.find_all('table')
    visited = set()

    for table in tables:
        print(table.find_all('tr'))
        tableLinks = table.find_all('a')
        print(tableLinks)
    # print(tables)
    return None

targetDomain = 'cs.rochester.edu'
# page = getPage('http://cs.rochester.edu/~omidb/nlpcalendar/')
page = getDynamicPage('https://www.cs.rochester.edu/~tetreaul/conferences.html')
print(page)
# print(extractUrls(page, targetDomain))
