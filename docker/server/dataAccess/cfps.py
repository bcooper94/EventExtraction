from pymongo import MongoClient
import dateutil.parser as dateParser
import dataAccess.models.cfp as cfp
import json

database = [{
    'id': 1,
    'url': 'http://www.google.com/',
    'conferenceName': 'Google Conference',
    'conferenceDate': '2017-01-02'
}, {
    'id': 2,
    'url': 'http://www.msn.com/',
    'conferenceName': 'MSN Conference',
    'conferenceDate': '2017-05-14'
}]

DB_NAME = 'CFPs'
CFP_COLLECTION = 'cfp_collection'
MONGO_HOST = '172.18.0.1'
MONGO_PORT = 27000
client = None


class CFPClient:
    def __init__(self):
        global client
        # self.client = MongoClient()
        if client is None:
            client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.db = client[DB_NAME]

    def search_cfps(self, query: str):
        return [cfp.CFP(result).serialize()
                for result in self.db[CFP_COLLECTION].find({'$text': {'$search': query}})]

    def get_cfp(self, id):
        return self.db[CFP_COLLECTION].find_one({'_id': id})

    def update_cfp(self, cfp):
        updated_cfp = None
        filtered_cfps = list(filter(lambda cfp: id == cfp['id'], database))
        if len(filtered_cfps) > 0:
            old_cfp = filtered_cfps[0]
            try:
                index = self._get_cfp_index(old_cfp['id'])
                database[index] = cfp
                updated_cfp = cfp
            except ValueError:
                print('No CFP with id {} found'.format(cfp['id']))

        return updated_cfp

    def delete_cfp(self, id):
        pass

    def create_cfp(self, cfp):
        if type(cfp) is dict:
            cfp = cfp.CFP(cfp)
        elif type(cfp) is not cfp.CFP:
            raise ValueError('Invalid cfp type')
        if cfp.id is not None:
            raise ValueError('CFP must not have an id property when being created')
        else:
            self.db[CFP_COLLECTION].insert_one(cfp.serialize())

    def create_many_cfps(self, cfp_list: list):
        all_cfps = [cfp.CFP(cfp).serialize() for cfp in cfp_list]
        self.db[CFP_COLLECTION].insert_many(all_cfps)

    def _get_cfp_index(self, id):
        for pos, cfp in enumerate(database):
            if id == cfp['id']:
                return pos

        raise ValueError('No CFP with id {} found.'.format(id))


def convert_date(date):
    return dateParser.parse(date).isoformat()


def convert_corpus_site(site):
    converted = {}
    if 'link' in site:
        converted[cfp.URL] = site['link']
    if 'people' in site:
        converted[cfp.PEOPLE] = site['people']
    if 'where' in site:
        converted[cfp.LOCATION] = site['where']
    if 'start' in site and site['start']:
        converted[cfp.CONFERENCE_START] = convert_date(site['start'])
    if 'stop' in site and site['stop'] is not None:
        converted[cfp.CONFERENCE_END] = convert_date(site['stop'])
    if 'topics' in site:
        converted[cfp.TOPICS] = site['topics']
    if 'email' in site:
        converted[cfp.EMAIL] = site['email']
    if 'submission deadline' in site and site['submission deadline'] is not None:
        converted[cfp.SUBMISSION_DATE] = convert_date(site['submission deadline'])
    if 'submissionLink' in site:
        converted[cfp.SUBMISSION_LINK] = site['submissionLink']
    if 'importantLinks' in site:
        converted[cfp.IMPORTANT_LINKS] = site['importantLinks']
    return converted


def insert_corpus(jsonPath):
    with open(jsonPath) as jsonFile:
        websites = json.load(jsonFile)
        converted_sites = [convert_corpus_site(site) for site in websites]
        # client = CFPClient()
        with open('corpus.json', 'w') as outfile:
            for site in converted_sites:
                outfile.write(json.dumps(site) + '\n')
        # success = client.create_many_cfps(converted_sites)
        # print(success)

if __name__ == '__main__':
    insert_corpus('../corpus/output.json')
#     client = CFPClient()
#     results = [str(CFP(result)) for result in client.search_cfps('acm')]
#     print('Results:', results)
