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


def _label_feature(site_features: list):
    site, date_features = site_features
    return site, label_date_features(date_features, site)


def label_features(date_features: list):
    return threadPool.map(_label_feature, date_features)


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
        websites = [site for site in threadPool.map(parsed_site, websites) if site is not None]
    return [site for site in websites]


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
    # print('Label probabilities:\n', label_probabilities)
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


def _predict_site_dates(labeled_site_features: list, model):
    site_dates = []
    site_probabilities = get_site_date_probabilities(labeled_site_features, model)
    # print('Labeled probdists for each site:')
    # for site, probabilities in site_probabilities:
    #     print('URL={}, probs={}'.format(site['link'], probabilities))

    for site, probabilities in site_probabilities:
        dates = {}
        for date_label in ['start', 'stop']:
            date_prediction, label, probability = get_max_probability_date(probabilities, date_label)
            dates[date_label] = (date_prediction, probability)
        site_dates.append((site, dates))
        # most_likely_start = get_max_probability_date(probabilities, 'start')
        # most_likely_stop = get_max_probability_date(probabilities, 'stop')
        # print('Site={}\nMost likely start:{}\nMost likely stop:{}\n'.format(
        #     site['link'], most_likely_start, most_likely_stop))
    return site_dates


def train_date_model(training_sites: list):
    all_date_features = [(site, extract_date_features(site['parsed_html'])) for site in training_sites]
    print('Labeling date features...')
    site_labeled_features = label_features(all_date_features)
    # site_labeled_features = [(labeled_site, label_date_features(date_features, labeled_site))
    #                          for (labeled_site, date_features) in all_date_features]
    collapsed_training_data = [(feature, label) for site, feature_list in site_labeled_features
                               for feature, label, date in feature_list if feature_list is not None]

    # TODO: Compare NaiveBayes, Maxent, and DecisionTree classifiers
    return nltk.MaxentClassifier.train(collapsed_training_data)


def predict_dates(sites: list, model):
    print('Extracting date features...')
    all_date_features = [(site, extract_date_features(site['parsed_html'])) for site in sites]
    print('Labeling date features...')
    site_labeled_features = label_features(all_date_features)
    return _predict_site_dates(site_labeled_features, model)


def get_prediction_accuracy(sites: list, model):
    site_features = [(site, extract_date_features(site['parsed_html'])) for site in sites]
    site_labeled_features = label_features(site_features)
    collapsed_features = [(feature, label) for site, feature_list in site_labeled_features
                          for feature, label, date in feature_list if feature_list is not None]

    return nltk.classify.accuracy(model, collapsed_features)


print('Loading training data...')
data = get_labeled_html('../wikicfp/dev.json')
random.shuffle(data)
training_count = int(len(data) * TRAINING_RATIO)

model = train_date_model(data[:training_count])
predicted_dates = predict_dates(data[training_count:], model)
for site, date_predictions in predicted_dates:
    print('Site={}, predictions={}'.format(site['link'], date_predictions))

date_classification_accuracy = get_prediction_accuracy(data[training_count:], model)
print('Date classification accuracy:', date_classification_accuracy)
