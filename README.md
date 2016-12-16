# EventExtraction

## Stanford CoreNLP Installation
In order to run the Baseline.py using Stanford CoreNLP, you have to add the following environmental variables:

CLASSPATH="<PROJECT_BASE_DIR>/EventExtraction/libs/stanford-ner-2015-12-09"

STANFORD_MODELS="<PROJECT_BASE_DIR>/EventExtraction/libs/stanford-ner-2015-12-09/classifiers/"

## SpaCy Installation
Run the following:
    pip install spacy
    python -m spacy.en.download all

## Running the Date Classifier
Navigate to the extraction subdirectory and run testDateClassifier.sh as follows:

./testDateClassifier.sh <TRIAL_COUNT>

For example, "./testDateClassifier.sh 5" runs the date classifier for 5 trials using the Naive Bayes classifier, then another 5 trials with the maximum entropy classifier for classifying dates.
