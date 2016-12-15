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
# PREDICTED_DATE_TYPES = [START_DATE, STOP_DATE]
PREDICTED_DATE_TYPES = [CONF_DATE]

starts_found = 0
start_not_found = 0
stops_found = 0
stop_not_found = 0

possible_starts_found = 0
possible_stops_found = 0
possible_starts = 0
possible_stops = 0


def extract_date_features(spacy_doc, context_width=5):
    features = []
    date_entities = [entity for entity in spacy_doc.ents if entity.label_ == 'DATE']

    for entity in date_entities:
        start = max(0, entity.start - 1)
        left_context = [word for word in spacy_doc[start - context_width:start]]
        right_context = [word for word in spacy_doc[entity.end:entity.end + context_width]]
        feature = {}
        for word in left_context:
            # if not word.is_stop:
            feature['left_' + str(word.lemma_).lower()] = True
            # feature[str(word.lemma_).lower()] = True
        for word in right_context:
            # if not word.is_stop:
            feature['right_' + str(word.lemma_).lower()] = True
            # feature[str(word.lemma_).lower()] = True

        normalized_date = normalizeDate(entity.text)
        if type(normalized_date) is tuple:
            feature['_is_range'] = True
        text_location = int((entity.start + entity.end) / 2)
        feature['_location'] = text_location

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

    if labeled_site is None:
        return None

    labeled_features = []
    found_start = False
    found_stop = False

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
            else:
                labeled = (feature, NONE_DATE, normalized_date)
            # if type(normalized_date) is tuple:
            #     normalized_start, normalized_stop = normalized_date
            #
            #     if normalized_start == normalized_stop:
            #         print('Tuple start == stop:', normalized_date)
            #     if normalized_start == start_date:
            #         print('Found start date from tuple:', normalized_start)
            #         labeled = (feature, 'start', normalized_start)
            #         found_start = True
            #     elif normalized_start == stop_date:
            #         print('Found stop date in normalized_start in tuple:', normalized_start)
            #         found_stop = True
            #         labeled = (feature, 'stop', normalized_start)
            #     elif normalized_stop == stop_date:
            #         print('Found end date from tuple:', normalized_stop)
            #         labeled = (feature, 'stop', normalized_stop)
            #         found_stop = True
            #     elif normalized_stop == start_date:
            #         print('Found start date in normalized_stop in tuple:', normalized_stop)
            #         found_start = True
            #         labeled = (feature, 'start', normalized_stop)
            #     else:
            #         labeled = (feature, 'none', normalized_date)
            # else:
            #     # print('Start={}, stop={}, normalized={}'.format(start_date, stop_date, normalized_date))
            #     if normalized_date == start_date:
            #         print('Found start date:', date_text)
            #         labeled = (feature, 'start', normalized_date)
            #         found_start = True
            #     elif normalized_date == stop_date:
            #         print('Found stop date:', date_text)
            #         labeled = (feature, 'stop', normalized_date)
            #         found_stop = True
            #     else:
            #         labeled = (feature, 'none', normalized_date)
            labeled_features.append(labeled)

        # if found_start:
        #     starts_found += 1
        # else:
        #     start_not_found += 1
        # if found_stop:
        #     stops_found += 1
        # else:
        #     stop_not_found += 1
        #
        # if not found_start and not found_stop:
        #     print("No start or stop found in", labeled_site['link'])
        # else:
        #     if not found_start:
        #         print("No start found in", labeled_site['link'])
        #     if not found_stop:
        #         print("No stop found in", labeled_site['link'])
        return labeled_features


def _label_feature(site_features: list):
    site, date_features = site_features
    return site, label_date_features(date_features, site)


def label_features(date_features: list):
    # return threadPool.map(_label_feature, date_features)
    return map(_label_feature, date_features)


def parsed_site(site):
    if 'html' in site and site['html'] is not None:
        soup = BeautifulSoup(site['html'], 'html.parser')
        if soup.body is not None:
            site['soup'] = soup
            site['parsed_html'] = nlp(soup.get_text())
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

                # lang_attr = soup.html['lang']
                # print('Language of {}: {}'.format(site['link'], lang_attr))
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
    # for website in websites:
    #     if 'parsed_html' in website:
    #         langs = [str(token.lang_) for token in website['parsed_html']]
    #         if any(lang != 'en' for lang in langs):
    #             print('Doc language for {}: {}'.format(website['link'],
    #                                                    website['parsed_html'][0].lang_))
    return [site for site in websites]


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

        date_candidates = [date for date, prob_dict in probabilities]
        # for date, prob_dict in probabilities:
        #     if type(date) is tuple:
        #         date_candidates.extend([str(date[0]), str(date[1])])
        #     else:
        #         date_candidates.append(str(date))
        normalized_site_start = normalizeDate(site['start'])
        normalized_site_stop = normalizeDate(site['stop'])
        conference_date = combine_start_stop_date(normalized_site_start, normalized_site_stop)
        print('Site conference_date={}, predictions={}'.format(conference_date, date_candidates))

        if conference_date not in date_candidates:
            print('No conference date found for', site['link'])
        # if str(normalized_site_start) not in str_dates:
        #     print('No start date found for', site['link'])
        # if str(normalized_site_stop) not in str_dates:
        #     print('No stop date found for', site['link'])

        for date_label in PREDICTED_DATE_TYPES:
            date_prediction, label, probability = get_max_probability_date(probabilities, date_label)
            dates[date_label] = (date_prediction, probability)
        if START_DATE in dates and STOP_DATE in dates:
            print('Checking if start and stop are tuples')
            start_date, start_probability = dates[START_DATE]
            stop_date, stop_probability = dates[STOP_DATE]
            true_start = start_date
            true_stop = stop_date

            if type(start_date) is tuple and type(stop_date) is tuple:
                print('Both start and end are tuples. Start={}, stop={}'.format(start_date, stop_date))
                if start_probability > stop_probability:
                    true_start, true_stop = start_date
                else:
                    true_start, true_stop = stop_date
            elif type(start_date) is tuple:
                # TODO: Check if defaulting to true_start/true_stop = the only range improves system
                true_start, true_stop = start_date
                print('Start is a tuple. Start={}, stop={}'.format(start_date, stop_date))
            elif type(stop_date) is tuple:
                true_start, true_stop = stop_date
                print('Stop is a tuple. Start={}, stop={}'.format(start_date, stop_date))

            dates[START_DATE] = true_start
            dates[STOP_DATE] = true_stop

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

    # Toss sites that we can't label with both a start and stop date
    # filtered_features = []
    # for site, feature_list in site_labeled_features:
    #     has_start = False
    #     has_stop = False
    #     for feature, label, date in feature_list:
    #         if label == START_DATE:
    #             has_start = True
    #         elif label == STOP_DATE:
    #             has_stop = True
    #     if has_start and has_stop:
    #         filtered_features.append((site, feature_list))
    # print('Filtered {} training sites down to {}'.format(len([feature for feature in site_labeled_features]), len(filtered_features)))
    # collapsed_training_data = [(feature, label) for site, feature_list in filtered_features
    #                            for feature, label, date in feature_list if feature_list is not None]
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
        # normalized_site_date = normalizeDate(site[date_type])
        site_start = normalizeDate(site['start'])
        site_stop = normalizeDate(site['stop'])
        conference_date = combine_start_stop_date(site_start, site_stop)
        if conference_date is not None and date_prediction_confidence[date_type] is not None:
            date_prediction, confidence = date_prediction_confidence[date_type]
            # prediction = date_prediction[date_type]
            # if type(prediction) is tuple:
            #     print('Comparing actual={} to prediction={} - {}'.format(
            #         conference_date, start.isoformat(), stop.isoformat()))
            # else:
            #     print('Comparing actual={} to prediction={}'.format(normalized_site_date.isoformat(),
            #                                                         prediction.isoformat()))
            date_is_correct = conference_date == date_prediction
            print('Site={}, Dates equal? {}. Actual conference date={} to prediction={}, confidence={}'.format(
                site['link'], date_is_correct, conference_date,
                date_prediction, confidence
            ))
    else:
        print('No start/stop in site:', site['link'])

    return date_is_correct


# Get the accuracy of dates compared to their known labels
def get_date_predict_accuracy(predicted_dates: list):
    total_counts = {}
    correct_counts = {}
    results = {}
    for label in PREDICTED_DATE_TYPES:
        total_counts[label] = 0
        correct_counts[label] = 0

    for site, date_prediction in predicted_dates:
        for label in PREDICTED_DATE_TYPES:
            # if label in site:
            total_counts[label] += 1
            if is_correct_date(site, label, date_prediction):
                correct_counts[label] += 1

    for label in PREDICTED_DATE_TYPES:
        try:
            results[label] = correct_counts[label] / total_counts[label]
        except ZeroDivisionError:
            results[label] = 'undefined'

    return results


def run_single_trial(data: list, trial_num):
    print('Running trial', trial_num)
    random.shuffle(data)
    # data = data[:30]
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

    predicted_dates = predict_dates(data[training_count:], model)
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

    date_extraction_accuracy = get_date_predict_accuracy(predicted_dates)
    print('Date extraction accuracy:', date_extraction_accuracy)
    print('Tested on {} docs'.format(len(data) - training_count))

    return date_extraction_accuracy, date_classification_accuracy


def run_trials(num_trials=5):
    print('Loading training data...')
    data = get_labeled_html('../wikicfp/dev.json')
    start = time.time()
    # results = [result for result in threadPool.map(lambda trial: run_single_trial(data, trial), range(num_trials))]
    results = [result for result in map(lambda trial: run_single_trial(data, trial), range(num_trials))]
    print('Trial run time:', time.time() - start)
    return results


if __name__ == '__main__':
    num_trials = 5
    if len(sys.argv) > 2:
        num_trials = int(sys.argv[2])

    results = run_trials(num_trials)
    classification_accuracy = [classify_acc for extraction_acc, classify_acc in results]
    date_extraction_accuracy = [extraction_acc[CONF_DATE] for extraction_acc, classify_acc in results]
    print('Classification accuracies:', classification_accuracy)
    print('Classification average accuracy:', sum(classification_accuracy) / len(classification_accuracy))
    print('Date extraction accuracies:', date_extraction_accuracy)
    print('Date extraction average accuracy:', sum(date_extraction_accuracy) / len(date_extraction_accuracy))
