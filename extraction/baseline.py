import re
import random


class Extractor:
    def __init__(self, docs: list):
        random.seed(356)
        self.docs = [doc for doc in docs]
        random.shuffle(self.docs)

    def crossValidate(self, folds=10, trainRatio=0.75):
        trainCount = int(len(self.docs) * trainRatio)
        trainingDocs = self.docs[:trainCount]
        testingDocs = self.docs[trainCount:]

        for i in range(folds):
            pass

    def train(self, trainRatio=0.75):
        trainCount = int(len(self.docs) * trainRatio)
        trainingDocs = self.docs[:trainCount]
        pass

    def test(self, trainRatio=0.75):
        trainCount = int(len(self.docs) * trainRatio)
        testingDocs = self.docs[trainCount:]
        pass


class Document:
    def __init__(self):
        pass

    def getFeatures(self):
        return {}
