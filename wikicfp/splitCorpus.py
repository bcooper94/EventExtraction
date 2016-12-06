import json
import random


def split_corpus(corpus_file: str, dev_ratio=0.8):
    with open(corpus_file) as file:
        corpus = json.load(file)
        random.seed(35)
        random.shuffle(corpus)
        dev_count = int(len(corpus) * dev_ratio)
        dev_set = corpus[:dev_count]
        test_set = corpus[dev_count:]

        with open('dev.json', 'w') as dev:
            json.dump(dev_set, dev, indent=3, separators=(',', ': '))
        with open('test.json', 'w') as test:
            json.dump(test_set, test, indent=3, separators=(',', ': '))


if __name__ == '__main__':
    split_corpus('output.json')
