import json
from baseline import BaselineExtractor
from extractor import EventExtractor


class CFPEvaluator:
    def __init__(self, jsonPath):
        with open(jsonPath) as jsonFile:
            self.websites = json.load(jsonFile)

        for site in self.websites:
            site['baseline'] = BaselineExtractor(site['html'])
            # site['experimental'] = EventExtractor(site['html'])

    def evaluateBaseline(self):
        results = {'location': 0, 'conferenceDate': 0}
        print('Site: ', self.websites[0].keys())
        validWebsites = [site for site in self.websites if site['baseline'].isValidDocument]
        validCount = len(validWebsites)

        for site in validWebsites:
            baseline = site['baseline']
            if 'conference' in baseline.dates and baseline.dates['conference'] == site['when']:
                results['conferenceDate'] += 1
            if baseline.location == site['when']:
                results['location'] += 1

            for key in site:
                if key != 'html':
                    print('{}: {}'.format(key, str(site[key])))
            print()

        for key in results:
            results[key] /= validCount
        return results


def isPdf(site):
    html = site['html']
    return html.startswith('%PDF')


evaluator = CFPEvaluator('../wikicfp/output.json')
print('Results:', evaluator.evaluateBaseline())
