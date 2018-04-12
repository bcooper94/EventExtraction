import datetime
from concurrent.futures import ThreadPoolExecutor
import json
from baseline import BaselineExtractor
from extractor import EventExtractor
from normalize import normalizeDate

threadPool = ThreadPoolExecutor(max_workers=4)

class CFPEvaluator:
    def __init__(self, jsonPath):
        with open(jsonPath) as jsonFile:
            print('opening websites from json')
            self.websites = json.load(jsonFile)

        # self.websites = [site for site in threadPool.map(self._createEventExtractor, self.websites[:50])]
        self.websites = [site for site in map(self._createEventExtractor, self.websites[:50])]
        # self.websites = [EventExtractor(site['html'], site['link'], site) for site in self.websites[:50]]
        # self.websites = [BaselineExtractor(site['html'], site['link'], site) for site in self.websites[:50]]
        # print(self.websites)

    def _createEventExtractor(self, site):
        # site['experimental'] = EventExtractor(site['html'], site['link'], site)
        site['baseline'] = BaselineExtractor(site['html'], site['link'], site)
        return site

    def evaluateTopicMatch(self):
        totalTopics = len(self.websites)
        extractionsWithTopics = [site for site in self.websites
                                 if site['experimental'] is not None
                                 and site['experimental'].topics is not None
                                 and len(site['experimental'].topics) > 0]
        for site in extractionsWithTopics:
            print('Found topics:', site['experimental'].topics)
        print('Out of {} sites, extracted topics for {} sites'.format(totalTopics,
                                                                      len(extractionsWithTopics)))


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
        # print('Site: ', self.websites[0].keys())


        validWebsites = [site for site in self.websites
                         if extractor in site and site[extractor].isValidDocument]
        for site in self.websites:
            print(site[extractor])
        validCount = len(validWebsites)

        if validCount == 0:
            print('NO VALID WEBSITES')
            return results

        for site in validWebsites:
            self._evaluate(site[extractor], site, results)

        for key in results:
            if validCount == 0:
                results[key] = 0
            else:
                results[key] /= validCount
        return results

    def _evaluate(self, extractor, site, results):
        # if 'conference' in extractor.dates:
        #     print('TWO DATES:')
        #     print(extractor.dates['conference'])
        #     print(site['start'])
        #     print('NORMALIZED:')
        #     if type(extractor.dates['conference']) is tuple:
        #         print(normalizeDate(extractor.dates['conference'][0]))
        #     else:
        #         print(normalizeDate(extractor.dates['conference']))
        #     print(normalizeDate(site['start']))
        #     print("LOCATION")
        #     print(extractor.location)
        #     print('LABELED LOC')
        #     print(site['where'])

        if 'conference' in extractor.conference_start:
            extractedDate = extractor.conference_start['conference']
            if type(extractedDate) is tuple:
                extractedDate = extractedDate[0]
            if normalizeDate(extractedDate) == normalizeDate(site['start']):
                results['conferenceDate'] += 1

        extractedLoc = extractor.location
        labeledLoc = site['where']
        if extractedLoc:
            extractedLoc = extractedLoc.replace(' ', '').replace(',', '')
        if labeledLoc:
            labeledLoc = labeledLoc.replace(' ', '').replace(',', '')
        if extractedLoc == labeledLoc:
            results['location'] += 1

        # if 'conference' in extractor.dates and extractor.dates['conference'] == site['start']:
        #     results['conferenceDate'] += 1
        # if extractor.location == site['where']:
        #     results['location'] += 1

        # for key in site:
        #     if key != 'html':
        #         print('{}: {}'.format(key, str(site[key])))
        # print()


def isPdf(site):
    html = site['html']
    return html.startswith('%PDF')

start = datetime.datetime.now()
evaluator = CFPEvaluator('../corpus/output.json')
print('Results:', evaluator.evaluate(True))
evaluator.printResults()
print('Evaluated in {}'.format(datetime.datetime.now() - start))
# evaluator.evaluateTopicMatch()
