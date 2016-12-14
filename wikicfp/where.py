# Author: Joey Wilson

import json
import nltk
import bs4
import sys
import random

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

service = discovery.build('language', 'v1', credentials=GoogleCredentials.get_application_default())

#debug
def json_print(obj):
   print(json.dumps(obj, indent=3))

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

def is_closer(index, a, b):
   a_dist = index - a['text']['beginOffset']
   b_dist = index - b['text']['beginOffset']
   if b_dist < 0:
      b_dist = 9999999
   if a_dist < b_dist:
      return a
   return b

def get_locations_from_google(text):
   global service

   locations = []
   
   service_request = service.documents().analyzeEntities(
      body={
         'document': {
            'type': 'PLAIN_TEXT',
            'content': text,
         },
         'encodingType': 'UTF32'
      }
   )
   try:
      response = service_request.execute()
   except:
      print('Exception', sys.exc_info())
      return locations   

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

   locations = []
   if page == None:
      return locations 

   text = bs4.BeautifulSoup(page, 'html.parser').get_text()
 

   possible_locations = get_locations_from_google(text)

   for l in possible_locations:
      name = l['name']
      mentions = l['mentions']
      if is_state_or_country(name, states, countries):
         for c in get_cities(name, mentions, possible_locations):
            locations.append({'city': c, 'country_or_state': name})

   for l in locations:
      ccs = '{}, {}'.format(l['city'], l['country_or_state'])
      index = 0
      index = text.find(ccs, index)
      l['index'] = []
      while index != -1:
         l['index'].append(index)
         l['context'] = nltk.word_tokenize(text[index-50: index])
         index = text.find(ccs, index+1)

   return locations

def extract_features(location):
   features = {}

   #json_print(location)
  
   if 'index' in location.keys(): 
      for index in location['index']:
         for i in range(1,10):
            if index < i*1000:
               features['{} <= index < {}'.format(i-1, i)] = True
   else:
      features['No index'] = True

   if 'context' in location.keys():
      for w in location['context']:
         features['contains({})'.format(w)] = True
   else:
      features['No context'] = True

   return features

   
def build_feature_list(data, states, countries):
   feature_list = []
   
   for d in data:
      print(d['link'])
      if d['where']:
         ccs = d['where'].split(',')
         if len(ccs) >= 2:
            if len(ccs) == 3 and not is_state_or_country(ccs[1], states, countries):
               print('ccs length 3 ', ccs)
               ccs[1] = ccs[2] 
            city = ccs[0].strip()
            country_or_state = ccs[1].strip()
            locations = get_locations(d['html'], states, countries)
            print(city, country_or_state)
            if len(locations) == 0:
               print('No locations found')
            else:
               for l in locations:
                  answer = False
                  if l['city'] == city and l['country_or_state'] == country_or_state:
                     answer = True
                  feature_list.append((extract_features(l), answer))
         else:
            print('No city or country: {}'.format(ccs))
      else:
         print('No where found')

   return feature_list

def run(training_data, test_data, states, countries):

   training_features = build_feature_list(training_data, states, countries)
   test_features = build_feature_list(test_data, states, countries)
   
   nb = nltk.NaiveBayesClassifier.train(training_features)
   me = nltk.MaxentClassifier.train(training_features)
   dt = nltk.DecisionTreeClassifier.train(training_features)

   print(len(training_features))
   print(len(test_features))

   for classifier in [nb, me, dt]:

      tp = 0
      fp = 0
      tn = 0
      fn = 0
      for t in test_features:
         guess = classifier.classify(t[0])
         if t[1] == True:
            if guess == True:
               tp += 1
            else:
               fn += 1
         elif t[1] == False:
            if guess == False:
               tn += 1
            else:
               fp += 1
         else:
            raise 'Broken'

      accuracy = (tp+tn)/len(test_features) 
      precision = float(tp)/(tp+fp)
      recall = float(tp)/(tp+fn)
      f1 = 2 * ((precision*recall)/(precision+recall))

      print('''
         Location Results
         Accuracy: {}
         Precision: {}
         Recall: {}
         f1: {}
         \n
      '''.format(accuracy, precision, recall, f1))

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

   data = cfps 

   random.shuffle(data)   
   
   si = int(len(data)/4)
   run(data[si:], data[0:si], states, countries)
 

if __name__ == '__main__':
   main()
