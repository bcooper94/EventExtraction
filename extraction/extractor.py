import nltk
import re
from bs4 import BeautifulSoup
from bs4.element import Tag
from nltk.tag import StanfordNERTagger
from nltk.corpus import wordnet as wn
from functools import reduce
from baseline import ConferenceExtractorBase

months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
          'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec']

'''
Fields:
    people
    location
    dates
    conference
    topics
'''


class EventExtractor(ConferenceExtractorBase):
    def __init__(self, html):
        ConferenceExtractorBase.__init__(self)
        soup = BeautifulSoup(html, 'html.parser')
        txt = soup.body.get_text()

        tokenizedText = nltk.word_tokenize(txt)
        # words = [word for word in text if word.lower() not in stopwords.words('english') and word.strip()]
        # pos = nltk.pos_tag(words)
        # print(words)
        stanfordTagger = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
        # ner = st.tag(words)
        namedEntities = stanfordTagger.tag(tokenizedText)
        namedEntities = [entity for entity in namedEntities if entity[1] != 'O']

        # Found on http://emailregex.com/
        self.email = self._extract_first_email(txt)

        # TODO: Extract organization from the page's copyright notice in our actual event extractor?
        # organizations = [tag for tag in namedEntities if tag[1] == 'ORGANIZATION']
        self.people = [tag for tag in namedEntities if tag[1] == 'PERSON']

        # Location: take the first entity tagged with LOCATION
        self.location = self._extract_first_entity(namedEntities, 'LOCATION')

        # Text = nltk.Text(tokenizedText)
        # conference = ['conference', 'association']

        abstractDate = ['abstract', 'summary', 'proposal']
        paperDate = ['paper', 'final']
        conferenceDate = ['conference', 'event', 'time', 'held', 'hosted']
        host = ['host']

        dates = self._extract_dates(txt)
        conference = self._extract_first_entity(namedEntities, 'ORGANIZATION')
        if len(conference) > 0:
            self.conference = conference
        self.topics = self._extract_topics(soup.body)

        self.dates = {}
        if len(dates) == 1:
            self.dates = {'conference': list(dates)[0]}
        else:
            dates = self._label_entities(txt, self._extract_dates(txt), [abstractDate, paperDate, conferenceDate])
            for date, key in dates:
                self.dates[key] = date
                # for date in dates:
                #     print(get_context(txt, date, 20))

    # ner = nltk.ne_chunk(pos)
    # print(ner)

    def __str__(self):
        return '<ConferenceExtractor conference={} locations=[{}]>'.format(self.conference, self.location)

    def _extract_first_entity(self, ner, entity):
        start = False
        entities = []

        for tag in ner:
            if start and tag[1] != entity:
                break

            start = tag[1] == entity
            if start:
                entities.append(tag[0])
        return reduce(lambda string, entity: '{} {}'.format(string, entity), entities)

    # Baseline topics extractor: only look for a list of topics after the keyword "topics"
    def _extract_topics(self, soup: BeautifulSoup):
        pattern = re.compile(r'(topics?)|(subjects?)')
        for element in soup.recursiveChildGenerator():
            # Only start search for lists of topics if "topics" is present, as in white paper
            if element.string is not None and pattern.match(str(element.string).lower()) is not None:
                return self._get_topic_list(element)
        return None

    def _get_topic_list(self, soup: BeautifulSoup):
        topics = []
        list = soup.find_next_sibling('ol') or soup.find_next_sibling('ul')
        if list is not None:
            topics = [element.string for element in list.contents if type(element) is Tag]
        return topics

    def _label_entities(self, text, entities, entity_labels):
        labeled_entities = []

        for entity in entities:
            # print(entity)
            context = self._get_context(text, entity).lower()
            if ':' in context:
                context = context[:context.find(':')]
            # print('context:  ' + context)
            for labelList in entity_labels:
                seen = False
                for label in labelList:
                    if label in context:
                        labeled_entities.append((entity, labelList[0]))
                        seen = True
                        break
                if seen:
                    break

        return labeled_entities

    # get's the context surrounding an input phrase
    # had to make this because nltk is stupid and doesn't support phrases when context searching
    def _get_context(self, text, phrase, range=30):
        beg = text.find(phrase)
        beg = beg if beg - range > 0 else 0
        end = beg + len(phrase)
        end = end if range + end < len(text) else len(text)

        return text[beg - range: end + range]

    # use a bunch of awful regexes to recognize some shitty dates off these damn sites
    def _extract_dates(self, text):
        dates = re.findall(r'(\d+/\d+/\d+)', text)  # '12/30/1994 and anstr(other one) 5/23/16')
        dates += re.findall(r'(\d+.*-\d+.*(([Jj]anuary)|([Ff]ebruary])|([Mm]arch)|([Aa]pril)|([Mm]ay)|([Jj]une)|'
                            r'([Jj]uly)|([Aa]ugust)|([Ss]eptember)|([Oo]ctober)|([Nn]ovember)|([Dd]ecember))'
                            r'\d*)', text)
        dates += re.findall(r'(\d{2}[/.-]\d{2}[/.-]\d{4})', text)  # '2-24-6575 and a second one 23/34/6445')
        # dates += re.findall(r"(\w+)\s(\d?\d),?\s?'?(\d{4})", text) #'November 23, 2018')
        dates += re.findall(r"\d{1,2}\s[A-Za-z]+,?\s?'?\d{4}",
                            text)  # "23 November 3942 and 3 November '48 and 23 November, 3948")
        dates += re.findall(r'(\d+\.\d+\.\d+)', text)  # 12.20.2001 format
        # dates += re.findall(r"(\w+)\s(\d{1,2})[trs][tdh]\s?,?\s?(\d{4})?", text)
        # ew = re.findall(r"((?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s\d{1,2}(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?)", text)
        ew = re.findall(r"((?:\d{2}\s)?(?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}"
                        r"(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s(?:\d{4}|\d{1,2})"
                        r"(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?"
                        r"(?:\s\d{4}?)?)", text)

        # regex isn't perfect, so it only keeps dates with words that are months
        for gross in ew:
            if gross[1].lower() in months:
                bool = False
                for date in dates:
                    bool = bool or gross[0] in date
                if not bool:
                    dates.append(gross[0])

        return set(dates)

    def _extract_first_email(self, text):
        firstEmail = None
        pattern = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        emails = pattern.findall(text)
        if len(emails) > 0:
            firstEmail = emails[0]

        return firstEmail


# soup = BeautifulSoup(open('cfp/Trusted Smart Contracts 2017.html'), 'html.parser')
# soup = BeautifulSoup(open('cfp/Corpus Historicus – The Body in_of History.html'), 'html.parser')
# soup = BeautifulSoup(open('cfp/Call For Papers – ERA Track _ SANER 2017.html'), 'html.parser')
# soup = BeautifulSoup(open('resources/era_track.html'), 'html.parser')
# soup = BeautifulSoup(open('resources/smart_contracts.html'), 'html.parser')
# soup = BeautifulSoup(open('resources/history.html'), 'html.parser')
# soup = BeautifulSoup(open('resources/embedded.html'), 'html.parser')
# soup = BeautifulSoup(open('resources/workshop2016.iwslt.org.html'), 'html.parser')
# doc = EventExtractor('resources/airccse.html')
# doc = EventExtractor('resources/iMT 2016.html')
print('-----------------------------')
print('REAL EXTRACTOR')
with open('resources/iMT 2016.html') as file:
    doc = EventExtractor(file.read())
    print('Topics: ', doc.topics)
    print('Conference location:', doc.location)
    # print('PEOPLE:', doc.people)
    print('Date:', doc.dates)
    print('Conference name:', doc.conference)
    print('Conference email:', doc.email)

# print('Topics: ', doc.topics)
# print('Conference location:', doc.locations)
# print('PEOPLE:', doc.people)
# print('Date:', doc.dates)
# print('Conference name:', doc.conferences)
# print('Conference email:', doc.email)
# topicSyn = wn.synset('topic.n.02')
# print(topicSyn)
# print('Hypernyms:', topicSyn.hypernyms())
# print('Hyponyms:', topicSyn.hyponyms())
# print('Definition:', topicSyn.definition())
# print('Lemma:', topicSyn.lemmas())
