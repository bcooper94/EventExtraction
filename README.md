# EventExtraction

Developed by Brandon Cooper, Joey Wilson, and Tobias Bleisch

## Corpus

For information about the corpus and web scraper, refer to the README in the corpus subdirectory.

## Requirements Installation
Run the following:
    pip install -r requirements.txt

## Stanford CoreNLP Installation
In order to run the Baseline.py using Stanford CoreNLP, you have to add the following environmental variables:

CLASSPATH="<PATH_TO_PROJECT>/EventExtraction/libs/stanford-ner-2015-12-09"

STANFORD_MODELS="<PATH_TO_PROJECT>/EventExtraction/libs/stanford-ner-2015-12-09/classifiers/"

## SpaCy Installation
Assuming you have used pip to install the requirements, run the following:
    python3 -m spacy.en.download all

For more information, see https://spacy.io/docs/usage/

## Running the baseline CFP extractor
Navigate to the extraction subdirectory and run the following:
    python3 evaluation.py

NOTE: This will print a lot of results. At the bottom will be the accuracy results.

## Running the Date Classifier
Navigate to the extraction subdirectory and run testDateClassifier.sh as follows:

./testDateClassifier.sh <TRIAL_COUNT>

For example, "./testDateClassifier.sh 5" runs the date classifier for 5 trials using the Naive Bayes classifier, then another 5 trials with the maximum entropy classifier for classifying dates. The script will create an out.txt with the dateClassifier's output, and print

## Running the Location Classifier

To run the location system refer to the README in the location folder.