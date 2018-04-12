import json
import random
import nltk
import spacy
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

from normalize import normalizeDate

TRAINING_RATIO = 0.8

threadPool = ThreadPoolExecutor(max_workers=4)
nlp = spacy.load('en')

START_DATE = 'start'
STOP_DATE = 'stop'
CONF_DATE = 'conference_date'
NONE_DATE = 'none'

conference_dates_found = 0

starts_found = 0
start_not_found = 0
stops_found = 0
stop_not_found = 0

possible_starts_found = 0
possible_stops_found = 0
possible_starts = 0
possible_stops = 0


def get_results(true_pos, true_neg, false_pos, false_neg):
    accuracy = float(true_pos + true_neg) / (true_pos + true_neg + false_pos + false_neg)

    if (true_pos + false_pos) > 0:
        precision = float(true_pos) / (true_pos + false_pos)
    else:
        precision = 0.0
    if (true_pos + false_neg) > 0:
        recall = float(true_pos) / (true_pos + false_neg)
    else:
        recall = 0.0
    if precision > 0 and recall > 0:
        f1 = 2 * ((precision * recall) / (precision + recall))
    else:
        f1 = 0.0

    return {
        'accuracy': accuracy, 'precision': precision,
        'recall': recall, 'f1': f1
    }


def extract_date_features(spacy_doc, context_width=5):
    features = []
    date_entities = [entity for entity in spacy_doc.ents if entity.label_ == 'DATE']

    for entity in date_entities:
        start = max(0, entity.start - 1)
        left_context = [word for word in spacy_doc[start - context_width:start]]
        right_context = [word for word in spacy_doc[entity.end:entity.end + context_width]]
        feature = {}
        for word in left_context:
            feature['left_' + str(word.lemma_).lower()] = True
        for word in right_context:
            feature['right_' + str(word.lemma_).lower()] = True

        normalized_date = normalizeDate(entity.text)
        # if type(normalized_date) is tuple:
        #     feature['_is_range'] = True
        # text_location = int((entity.start + entity.end) / 2)
        # feature['_location'] = text_location

        # Toss this feature if we can't parse a date
        if normalized_date is not None:
            features.append((feature, normalized_date, entity.text))

    return features


def combine_start_stop_date(start, stop):
    combined_date = None
    if start is not None and stop is not None:
        if start == stop:
            combined_date = start
        else:
            combined_date = (start, stop)

    return combined_date


def label_date_features(date_features: list, labeled_site: dict):
    global starts_found
    global stops_found
    global start_not_found
    global stop_not_found
    global possible_starts
    global possible_starts_found
    global possible_stops
    global possible_stops_found
    global conference_dates_found

    correct_date_found = False

    if labeled_site is None:
        return None

    labeled_features = []

    if labeled_site is not None and 'start' in labeled_site and 'stop' in labeled_site:
        start_date = normalizeDate(labeled_site['start'])
        stop_date = normalizeDate(labeled_site['stop'])
        conference_date = combine_start_stop_date(start_date, stop_date)

        start_str = str(start_date)
        stop_str = str(stop_date)
        possible_dates = [str(normalized_date) for feature, normalized_date, date_text in date_features]
        possible_starts += 1
        possible_stops += 1
        if start_str in possible_dates:
            possible_starts_found += 1
        if stop_str in possible_dates:
            possible_stops_found += 1

        for feature, normalized_date, date_text in date_features:
            if normalized_date == conference_date:
                labeled = (feature, CONF_DATE, normalized_date)

                if not correct_date_found:
                    print('Correct date found for:', labeled_site['link'])
                    correct_date_found = True
                    conference_dates_found += 1
            else:
                labeled = (feature, NONE_DATE, normalized_date)

            labeled_features.append(labeled)
        return labeled_features


def _label_feature(site_features: list):
    site, date_features = site_features
    return site, label_date_features(date_features, site)


def label_features(date_features: list):
    # return threadPool.map(_label_feature, date_features)
    return [_label_feature(feature) for feature in date_features]


def parsed_site(site):
    if 'html' in site and site['html'] is not None:
        soup = BeautifulSoup(site['html'], 'html.parser')
        if soup.body is not None:
            site['soup'] = soup
            text = soup.get_text()
            site['parsed_html'] = nlp(text)
            return site
    return None


def determine_site_languages(sites: list):
    site_languages = []
    for site in sites:
        language = None
        if 'soup' in site:
            print('Determining language for', site['link'])
            soup = site['soup']
            if soup.html is not None and 'lang' in soup.html.attrs:
                lang_attr = soup.html.attrs['lang']
                print('Lang attrs:', lang_attr)
                language = str(lang_attr).lower()

            meta_tags = [tag for tag in soup.find_all('meta')
                         if 'lang' in tag or 'property' in tag
                         and 'locale' in str(tag['property']).lower()]
            if len(meta_tags) > 0:
                print('Language from meta tags in {}: {}'.format(site['link'], meta_tags[0]['content']))
        site_languages.append((site, language))
    return site_languages


def get_labeled_html(jsonPath: str):
    websites = None

    with open(jsonPath) as jsonFile:
        websites = json.load(jsonFile)
    if websites is not None:
        # TODO: Remove 50 site limit
        websites = [site for site in threadPool.map(parsed_site, websites) if site is not None]
        lang_labeled_sites = [(site, lang) for site, lang in determine_site_languages(websites)
                              if lang is None or lang.startswith('en')]
        print('Threw out {} sites b/c of language'.format(len(websites) - len(lang_labeled_sites)))
        unlabeled_sites = [site for site, lang in lang_labeled_sites if lang is None]
        print('Language not labeled for {} sites'.format(len(unlabeled_sites)))
        websites = [site for site, lang in lang_labeled_sites]

    return [site for site in websites]


# Get the highest probability date and its probability as a (date, probability) tuple
# label_probabilities: list of dicts
# label: dictionary key
def get_max_probability_date(label_probabilities: list):
    label_probabilities = [(date, label, probability[CONF_DATE])
                           for date, probability, label in label_probabilities
                           if label in probability]
    max_prob = (None, 0)
    max_label = None
    for date, label, probability in label_probabilities:
        if probability > max_prob[1]:
            max_prob = date, probability
            max_label = label
    return max_prob[0], max_label, max_prob[1]


def get_site_date_probabilities(site_features: list, model):
    test_label_probdists = [(site, [(date, model.prob_classify(feature))
                                    for feature, label, date in labeled_features])
                            for site, labeled_features in site_features]
    true_pos = 0
    false_pos = 0
    true_neg = 0
    false_neg = 0

    site_probabilities = []
    for site, probability_dists in test_label_probdists:
        site_start = normalizeDate(site[START_DATE])
        site_stop = normalizeDate(site[STOP_DATE])
        conference_date = combine_start_stop_date(site_start, site_stop)

        probability_list = []
        for date, probdist in probability_dists:
            prob_dict = {}
            for sample in probdist.samples():
                prob_dict[sample] = probdist.prob(sample)

            predicted_label = probdist.max()
            probability_list.append((date, prob_dict, predicted_label))
            print('Prediction={}, actual={}, label={}'.format(date, conference_date, predicted_label))

            if date == conference_date and predicted_label == CONF_DATE:
                print('True pos. Actual={}, comparison={}'.format(date, conference_date))
                true_pos += 1
            elif date == conference_date and predicted_label == NONE_DATE:
                print('False neg. Actual={}, comparison={}'.format(date, conference_date))
                false_neg += 1
            elif date != conference_date and predicted_label == CONF_DATE:
                print('False pos. Actual={}, comparison={}'.format(date, conference_date))
                false_pos += 1
            elif date != conference_date and predicted_label == NONE_DATE:
                print('True neg. Actual={}, comparison={}'.format(date, conference_date))
                true_neg += 1

        site_probabilities.append((site, probability_list))

    return site_probabilities, get_results(true_pos, true_neg, false_pos, false_neg)


def _predict_site_dates(labeled_site_features: list, model):
    site_dates = []
    site_probabilities, classifier_results = get_site_date_probabilities(labeled_site_features, model)

    for site, probabilities in site_probabilities:
        dates = {}

        date_candidates = [date for date, prob_dict, label in probabilities]
        normalized_site_start = normalizeDate(site['start'])
        normalized_site_stop = normalizeDate(site['stop'])
        conference_date = combine_start_stop_date(normalized_site_start, normalized_site_stop)
        print('Site conference_date={}, predictions={}'.format(conference_date, date_candidates))

        if conference_date not in date_candidates:
            print('No conference date found for', site['link'])

        date_prediction, label, probability = get_max_probability_date(probabilities)
        dates[CONF_DATE] = (date_prediction, probability, label)
        site_dates.append((site, dates))

    return site_dates, classifier_results


def train_date_model(training_sites: list):
    all_date_features = [(site, extract_date_features(site['parsed_html'])) for site in training_sites]
    print('Labeling date features...')
    site_labeled_features = label_features(all_date_features)
    print('Correct dates identified for {} out of {} sites'.format(conference_dates_found, len(training_sites)))
    collapsed_training_data = [(feature, label) for site, feature_list in site_labeled_features
                               for feature, label, date in feature_list if feature_list is not None]

    # TODO: Compare NaiveBayes and Maxent classifiers
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'nb':
        model = nltk.NaiveBayesClassifier.train(collapsed_training_data)
    else:
        model = nltk.MaxentClassifier.train(collapsed_training_data)

    return model


# Predict the conference start/end date and submission date for each site in sites
# Returns: [(site, {'start': ..., 'stop': ..., 'submission date':...}, ...]
def predict_dates(sites: list, model):
    print('Extracting date features...')
    all_date_features = [(site, extract_date_features(site['parsed_html'])) for site in sites]
    print('Labeling date features...')
    site_labeled_features = label_features(all_date_features)
    return _predict_site_dates(site_labeled_features, model)


# Get the classification accuracy of the model from a list of sites
def get_classification_accuracy(sites: list, model):
    site_features = [(site, extract_date_features(site['parsed_html'])) for site in sites]
    site_labeled_features = label_features(site_features)
    collapsed_features = [(feature, label) for site, feature_list in site_labeled_features
                          for feature, label, date in feature_list if feature_list is not None]

    return nltk.classify.accuracy(model, collapsed_features)


def is_correct_date(site, date_type: str, date_prediction_confidence: dict):
    date_is_correct = False
    if START_DATE in site and STOP_DATE in site:
        site_start = normalizeDate(site['start'])
        site_stop = normalizeDate(site['stop'])
        conference_date = combine_start_stop_date(site_start, site_stop)
        if conference_date is not None and date_prediction_confidence[date_type] is not None:
            date_prediction, confidence, label = date_prediction_confidence[date_type]
            date_is_correct = conference_date == date_prediction
            print('Site={}, Dates equal? {}. Actual conference date={} to prediction={}, confidence={}'.format(
                site['link'], date_is_correct, conference_date,
                date_prediction, confidence
            ))
    else:
        print('No start/stop in site:', site['link'])

    return date_is_correct


# Get the accuracy of dates compared to their known labels
def get_date_predict_results(predicted_dates: list):
    correct_counts = 0
    total_counts = 0

    for site, date_prediction in predicted_dates:
        total_counts += 1
        correct = is_correct_date(site, CONF_DATE, date_prediction)

        if correct:
            correct_counts += 1
    try:
        results = correct_counts / total_counts
    except ZeroDivisionError:
        results = 'undefined'

    return results


def run_single_trial(data: list, trial_num):
    print('Running trial', trial_num)
    random.shuffle(data)
    training_count = int(len(data) * TRAINING_RATIO)
    model = train_date_model(data[:training_count])

    try:
        print('Found {} starts out of {} total. Accuracy = {}'.format(starts_found, starts_found + start_not_found,
                                                                      starts_found / (starts_found + start_not_found)))
        print('Found {} stops out of {} total. Accuracy = {}'.format(stops_found, stops_found + stop_not_found,
                                                                     stops_found / (stops_found + stop_not_found)))
        print('There were {} possible starts out of {} total. Accuracy = {}'.format(
            possible_starts_found, possible_starts, possible_starts_found / possible_starts
        ))
        print('There were {} possible stops out of {} total. Accuracy = {}'.format(
            possible_stops_found, possible_stops, possible_stops_found / possible_stops
        ))
    except ZeroDivisionError:
        print('Division by zero')

    predicted_dates, classification_results = predict_dates(data[training_count:], model)
    for site, date_predictions in predicted_dates:
        if 'start' in site and 'stop' in site:
            start = normalizeDate(site['start'])
            stop = normalizeDate(site['stop'])
            if start is not None and stop is not None:
                print('Site={}, start={}, stop={}, predictions={}'.format(
                    site['link'], start, stop, date_predictions))
            else:
                print('Unable to determine start/stop for', site['link'])

        else:
            print('Unable to determine start/stop for', site['link'])

    date_classification_accuracy = get_classification_accuracy(data[training_count:], model)
    print('Date classification accuracy:', date_classification_accuracy)
    print('Classification results: accuracy={}, precision={}, recall={}, F1={}'.format(
        classification_results['accuracy'], classification_results['precision'],
        classification_results['recall'], classification_results['f1']
    ))

    date_extraction_accuracy = get_date_predict_results(predicted_dates)
    print('Date extraction accuracy:', date_extraction_accuracy)
    print('Tested on {} docs'.format(len(data) - training_count))

    # return date_extraction_results, date_classification_accuracy
    return date_extraction_accuracy, classification_results


def run_trials(num_trials=5):
    print('Loading training data...')
    data = get_labeled_html('../corpus/output.json')
    start = time.time()
    # results = [result for result in threadPool.map(lambda trial: run_single_trial(data, trial), range(num_trials))]
    results = [result for result in map(lambda trial: run_single_trial(data, trial), range(num_trials))]
    extraction_accuracies = [accuracy for accuracy, classify_results in results]
    classify_results = [classify_results for accuracy, classify_results in results]
    print('Trial run time:', time.time() - start)
    return extraction_accuracies, classify_results


if __name__ == '__main__':
    num_trials = 5
    if len(sys.argv) > 2:
        num_trials = int(sys.argv[2])

    extraction_accuracies, classify_results = run_trials(num_trials)
    classification_accuracy = [result['accuracy'] for result in classify_results]
    classify_precision = [result['precision'] for result in classify_results]
    classify_recall = [result['recall'] for result in classify_results]
    classify_f1 = [result['f1'] for result in classify_results]

    print('Classification precisions:', classify_precision)
    print('Classification recalls:', classify_recall)
    print('Classification F1s:', classify_f1)
    print('Classification accuracies:', classification_accuracy)
    print('Classification average accuracy:', sum(classification_accuracy) / len(classification_accuracy))
    print('Classification avg precision:', sum(classify_precision) / len(classify_precision))
    print('Classification avg recall:', sum(classify_recall) / len(classify_recall))
    print('Classification avg F1:', sum(classify_f1) / len(classify_f1))
    print('Date extraction accuracies:', extraction_accuracies)
    print('Date extraction average accuracy:', sum(extraction_accuracies) / len(extraction_accuracies))
