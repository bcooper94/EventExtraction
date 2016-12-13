import json
import random
import nltk
import spacy
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

from normalize import normalizeDate

TRAINING_RATIO = 0.8

threadPool = ThreadPoolExecutor(max_workers=4)
nlp = spacy.load('en')


def extract_date_features(spacy_doc, context_width=5):
    features = []
    date_entities = [entity for entity in spacy_doc.ents if entity.label_ == 'DATE']

    for entity in date_entities:
        start = max(0, entity.start - 1)
        left_context = [word for word in spacy_doc[start - context_width:start]]
        right_context = [word for word in spacy_doc[entity.end:entity.end + context_width]]
        feature = {}
        for word in left_context:
            feature['left_' + str(word)] = True
        for word in right_context:
            feature['right_' + str(word)] = True

        normalized_date = normalizeDate(entity.text)

        if normalized_date is not None:
            features.append((feature, normalized_date, entity.text))

    return features


def label_date_features(date_features: list, labeled_site: dict):
    if labeled_site is None:
        return None

    labeled_features = []
    found_start = False
    found_stop = False

    if labeled_site is not None and 'start' in labeled_site and 'stop' in labeled_site:
        start_date = normalizeDate(labeled_site['start'])
        stop_date = normalizeDate(labeled_site['stop'])
        for feature, normalized_date, date_text in date_features:
            if type(normalized_date) is tuple:
                normalized_start, normalized_stop = normalized_date

                if normalized_start == start_date:
                    # print('Found start date:', normalized_start)
                    labeled = (feature, 'start', normalized_start)
                    found_start = True
                elif normalized_stop == stop_date:
                    # print('Found end date:', normalized_stop)
                    labeled = (feature, 'stop', normalized_stop)
                    found_stop = True
                else:
                    labeled = (feature, 'none', normalized_date)
            else:
                # print('Start={}, stop={}, normalized={}'.format(start_date, stop_date, normalized_date))
                if normalized_date == start_date:
                    # print('Found start date:', date_text)
                    labeled = (feature, 'start', normalized_date)
                    found_start = True
                elif normalized_date == stop_date:
                    # print('Found stop date:', date_text)
                    labeled = (feature, 'stop', normalized_date)
                    found_stop = True
                else:
                    labeled = (feature, 'none', normalized_date)
            labeled_features.append(labeled)

        # if not found_start and not found_stop:
        #     print("No start or stop found in", labeled_site['link'])
        # else:
        #     if not found_start:
        #         print("No start found in", labeled_site['html'])
        #     if not found_stop:
        #         print("No stop found in", labeled_site['html'])
        return labeled_features


def parsed_site(site):
    if 'html' in site and site['html'] is not None:
        soup = BeautifulSoup(site['html'], 'html.parser')
        if soup.body is not None:
            site['parsed_html'] = nlp(soup.get_text())
            return site
    return None


def get_labeled_html(jsonPath: str):
    websites = None

    with open(jsonPath) as jsonFile:
        websites = json.load(jsonFile)
    if websites is not None:
        websites = [site for site in threadPool.map(parsed_site, websites[:50]) if site is not None]
        # valid_sites = []
        # for site in websites:
        #     parsed = parsed_site(site)
        #     if parsed is not None:
        #         valid_sites.append(parsed)
        # websites = valid_sites
    return [site for site in websites[:50]]


def train_date_classifier(feature_label_tuples: list):
    return nltk.MaxentClassifier.train(feature_label_tuples)


def classify_date(features: dict, model: nltk.NaiveBayesClassifier):
    return model.classify(features)


# Get the highest probability date and its probability as a (date, probability) tuple
# label_probabilities: list of dicts
# label: dictionary key
def get_max_probability_date(label_probabilities: list, label: str):
    label_probabilities = [(date, label, probability[label]) for date, probability in label_probabilities
                           if label in probability]
    print('Label probabilities:\n', label_probabilities)
    max_prob = (None, 0)
    for date, sample, probability in label_probabilities:
        if probability > max_prob[1]:
            max_prob = date, probability
    return max_prob[0], label, max_prob[1]


def get_site_date_probabilities(site_features: list, model):
    test_label_probdists = [(site, [(date, model.prob_classify(feature))
                                    for feature, label, date in labeled_features])
                            for site, labeled_features in site_features]
    # test_site_probabilities = [(site, [(date, [sample, probdist.prob(sample)
    #                                            for sample in probdist.samples()]))
    #                                    for date, probdist in probabilities])
    #                            for site, probabilities in test_label_probdists]

    site_probabilities = []
    for site, probability_dists in test_label_probdists:
        probability_list = []
        for date, probdist in probability_dists:
            prob_dict = {}
            for sample in probdist.samples():
                prob_dict[sample] = probdist.prob(sample)
            probability_list.append((date, prob_dict))
        site_probabilities.append((site, probability_list))

    return site_probabilities


print('Loading training data...')
training_data = get_labeled_html('../wikicfp/dev.json')
print('Extracting date features...')
training_date_features = [(site, extract_date_features(site['parsed_html'])) for site in training_data]
print('Labeling date features...')
site_labeled_features = [(labeled_site, label_date_features(date_features, labeled_site))
                         for (labeled_site, date_features) in training_date_features]
random.shuffle(site_labeled_features)
training_count = int(len(site_labeled_features) * TRAINING_RATIO)
training_site_features = site_labeled_features[:training_count]
test_site_features = site_labeled_features[training_count:]

collapsed_training_data = [(feature, label) for site, feature_list in training_site_features
                           for feature, label, date in feature_list if feature_list is not None]
collapsed_testing_data = [(feature, label) for site, feature_list in test_site_features
                          for feature, label, date in feature_list if feature_list is not None]

# feature_label_date_list = [(site, feature_label) for site, feature_list in
#                            [(labeled_site, label_date_features(date_features, labeled_site))
#                             for (date_features, labeled_site) in
#                             training_date_features]
#                            for feature_label in feature_list if feature_list is not None]
print('Finished labeling date features...')
# print('Date features:\n', labeled_features)

# random.shuffle(feature_label_date_list)
# training_count = int(len(feature_label_date_list) * TRAINING_RATIO)
# label_feature_tuples = [(feature, label) for (feature, label, date) in feature_label_date_list]


date_model = train_date_classifier(collapsed_training_data)
print('Date model accuracy:', nltk.classify.accuracy(date_model, collapsed_testing_data))

site_probabilities = get_site_date_probabilities(test_site_features, date_model)
print('Labeled probdists for each site:')
for site, probabilities in site_probabilities:
    print('URL={}, probs={}'.format(site['link'], probabilities))

# label_probdists = [(date, date_model.prob_classify(feature))
#                    for (feature, label, date) in feature_label_date_list[training_count:]]
# label_probabilities = [(date, [(sample, probdist.prob(sample)) for sample in probdist.samples()])
#                        for (date, probdist) in label_probdists]
# # print(label_probabilities)
# date_probabilities = []
#
# # print('Label probabilities:')
# for date, label_set_probability in label_probabilities:
#     prob_dict = {}
#     for label, probability in label_set_probability:
#         prob_dict[label] = probability
#         # print('{} = {}'.format(label, probability))
#     # print()
#     date_probabilities.append((date, prob_dict))
#

for site, probabilities in site_probabilities:
    print('Site={}'.format(site['link']))
    most_likely_start = get_max_probability_date(probabilities, 'start')
    most_likely_stop = get_max_probability_date(probabilities, 'stop')
    print('Site={}\nMost likely start:{}\nMost likely stop:{}\n'.format(
        site['link'], most_likely_start, most_likely_stop))
