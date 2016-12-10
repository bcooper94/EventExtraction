# Author: Joey Wilson

import json
import nltk
import bs4

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

#debug
def json_print(obj):
   print(json.dumps(obj, indent=3))

#def extract_features(page):
#   features = {}
#
#   return features
#
#   
#def build_feature_list(data):
#   feature_list = []
#   for d in data:
#      feature_list.append()

#def n_gram(index, text, n):
#   gram = []
#   for i in range(0, n):
#      gram.append(text[index+i])
#   return ' '.join(gram)
#
def is_state_or_country(text, states, countries):
   if text.upper() in states or text.upper() in countries:
      return True
   return False
#   if n_gram(index, text, 2) in states or n_gram(index, text, 2) in countries:
#      return True
#   if n_gram(index, text, 3) in states or n_gram(index, text, 3) in countries:
#      return True
#   if n_gram(index, text, 4) in states or n_gram(index, text, 4) in countries:
#      return True
#   return False 

def is_closer(index, a, b):
   a_dist = index - a['text']['beginOffset']
   b_dist = index - b['text']['beginOffset']
   if b_dist < 0:
      b_dist = 9999999
   if a_dist < b_dist:
      return a
   return b

def get_locations_from_google(text):
   credentials = GoogleCredentials.get_application_default()
   service = discovery.build('language', 'v1', credentials=credentials)
   
   service_request = service.documents().analyzeEntities(
      body={
         'document': {
            'type': 'PLAIN_TEXT',
            'content': text,
         },
         'encodingType': 'UTF32'
      }
   )
   response = service_request.execute()
   
   locations = []
   for e in response['entities']:
      if e['type'] == 'LOCATION':
         locations.append(e)
   return locations  
   
def get_cities(name, mentions, locations):
   
   cities = []

   for m in mentions:
      _min = None
      index = m['text']['beginOffset']
      for l in locations:
         if name != l['name']:
            for mm in l['mentions']:
               if _min == None:
                  _min = mm
               _min = is_closer(index, _min, mm) 
      cities.append(_min['text']['content'])

   return cities

def get_locations(page, states, countries):

   text = bs4.BeautifulSoup(page, 'html.parser').get_text()
 
   locations = []

   possible_locations = get_locations_from_google(text)

   for l in possible_locations:
      name = l['name']
      mentions = l['mentions']
      if is_state_or_country(name, states, countries):
         for c in get_cities(name, mentions, possible_locations):
            locations.append({'city': c, 'country_or_state': name})

   for l in locations:
      _str = '{}, {}'.format(l['city'], l['country_or_state'])
      index = 0
      index = text.find(_str, index)
      while index != -1:
         l['context'] = nltk.word_tokenize(text[index-50: index])
         index = text.find(_str, index+1)

   json_print(locations)

   return locations

#   locations = []
#   for i in range(2, len(text)):
#      if text[i-1] == ',' and is_state_country(i, text, states, countries):
#         locations.append({
#            'city': text[i-2],
#            'country_or_state': text[i],
#            'context': text[i-10: i]
#         })
#         print('{}, {}\nContext: {}'.format(text[i-2], text[i], text[i-10: i]))
#
#   return locations
 
#def run(training_data, test_data):

   #training_features = build_feature_list(training_data)
   #test_features = build_feature_list(test_data)
   
   #classifier = nltk.NaiveBayesClassifier.train(training_features)
   #print('Location: ', nltk.classify.accuracy(classifier, test_features))

def main():
   f = open('./output.json')
   cfps = json.loads(f.read())
   f.close()

   f = open('./locations/states.json')
   states = json.loads(f.read())
   f.close()
  
   f = open('./locations/countries.json')
   countries = json.loads(f.read())
   f.close()

   cfp = cfps[0]

   print('Link: {} Where: {}'.format(cfp['link'], cfp['where']))

   get_locations(cfp['html'], states, countries)


if __name__ == '__main__':
   main()
