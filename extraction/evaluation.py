import datetime
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
import json
from baseline import BaselineExtractor
from extractor import EventExtractor

# threadPool = ThreadPool(4)
threadPool = ThreadPoolExecutor(max_workers=4)

class CFPEvaluator:
    def __init__(self, jsonPath):
        with open(jsonPath) as jsonFile:
            self.websites = json.load(jsonFile)


        self.websites = [site for site in threadPool.map(self._createEventExtractor, self.websites[:25])]
        print('Self.websites:', str(self.websites))

    def _createEventExtractor(self, site):
        site['experimental'] = EventExtractor(site['html'], site['link'])
        return site

    def printResults(self):
        for page in self.websites:
            if 'experimental' in page:
                site = page['experimental']
                if site.isValidDocument:
                    print(str(site), '\n')

    def evaluate(self, baseline=False):
        if baseline:
            extractor = 'baseline'
        else:
            extractor = 'experimental'

        results = {'location': 0, 'conferenceDate': 0}
        print('Site: ', self.websites[0].keys())
        validWebsites = [site for site in self.websites
                         if extractor in site and site[extractor].isValidDocument]
        validCount = len(validWebsites)

        for site in validWebsites:
            self._evaluate(site[extractor], site, results)

        for key in results:
            results[key] /= validCount
        return results

    def _evaluate(self, extractor, site, results):
        if 'conference' in extractor.dates and extractor.dates['conference'] == site['start']:
            results['conferenceDate'] += 1
        if extractor.location == site['where']:
            results['location'] += 1

        # for key in site:
        #     if key != 'html':
        #         print('{}: {}'.format(key, str(site[key])))
        # print()


def isPdf(site):
    html = site['html']
    return html.startswith('%PDF')

start = datetime.datetime.now()
evaluator = CFPEvaluator('../wikicfp/output.json')
print('Results:', evaluator.evaluate())
evaluator.printResults()
print('Evaluated in {}'.format(datetime.datetime.now() - start))
