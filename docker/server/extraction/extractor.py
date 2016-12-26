import nltk
import spacy
import re
import json
import random
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from bs4.element import Tag
from nltk.tag import StanfordNERTagger
from nltk.corpus import wordnet as wn
from functools import reduce
from urllib.parse import urljoin
from baseline import ConferenceExtractorBase
from normalize import normalizeDate

threadPool = ThreadPoolExecutor(max_workers=4)

months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
          'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec']

nlp = spacy.load('en')

'''
Fields:
    people
    location
    dates
    conference
    topics
'''
class EventExtractor(ConferenceExtractorBase):
    def __init__(self, html, url, labeled_site=None):
        # Get rid of weird unicode symbols
        filtered_html = ''
        if html is not None:
            for char in html:
                try:
                    char.encode('ascii')
                    filtered_html += char
                except Exception:
                    pass
        else:
            filtered_html = None

        ConferenceExtractorBase.__init__(self, filtered_html, url, labeled_site)

        if not self.isValidDocument:
            return

        txt = self.webpage.body.get_text()
        tokenizedText = nltk.word_tokenize(txt)
        stanfordTagger = StanfordNERTagger(model_filename='english.all.3class.distsim.crf.ser.gz')
        namedEntities = stanfordTagger.tag(tokenizedText)
        # dateEntities = collapse_entities(namedEntities, 'DATE')
        # dateEntities = split_dates(dateEntities)
        # print('Dates for {}:\n'.format(labeled_site['link']), dateEntities)
        namedEntities = [entity for entity in namedEntities if entity[1] != 'O']
        # dateEntities = self._extract_first_entity(namedEntities, 'DATE')
        spacy_doc = nlp(txt)
        # date_features = extract_date_features(spacy_doc)
        # labeled_features = label_date_features(date_features, labeled_site)

        # date_locations = self._extract_dates(txt)

        # Found on http://emailregex.com/
        self.email = self._extract_first_email(txt)

        # organizations = [tag for tag in namedEntities if tag[1] == 'ORGANIZATION']
        self.people = [tag for tag in namedEntities if tag[1] == 'PERSON']

        # Location: take the first entity tagged with LOCATION
        self.location = self._extract_first_entity(namedEntities, 'LOCATION')

        # conference = ['conference', 'association']

        abstractDate = ['abstract', 'summary', 'proposal']
        paperDate = ['paper', 'final']
        conferenceDate = ['conference', 'event', 'time', 'held', 'hosted']
        host = ['host']

        conference = self._extract_first_entity(namedEntities, 'ORGANIZATION')
        if conference is not None and len(conference) > 0:
            self.conference = conference
        self.topics = self._extract_topics(self.webpage.body)

        self.dates = {}
        dates = self._extract_dates(txt)
        if len(dates) == 1:
            self.dates = {'conference': list(dates)[0]}
        else:
            dates = self._label_entities(txt, self._extract_dates(txt), [abstractDate, paperDate, conferenceDate])
            for date, key in dates:
                self.dates[key] = date
                # for date in dates:
                #     print(get_context(txt, date, 20))
        labeledLinks = self._get_labeled_links()
        self.email = []
        for link in labeledLinks:
            linkLabel = link['label']
            if self.submissionLink is None and linkLabel == 'submissionDate':
                self.submissionLink = link['url']
            elif linkLabel == 'faq':
                self.importantLinks.append(link['url'])
            elif linkLabel == 'email':
                self.email.append(label_email_feature(link))

    def _extract_first_entity(self, ner, entity):
        start = False
        entities = []
        firstEntity = None

        for tag in ner:
            if start and tag[1] != entity:
                break

            start = tag[1] == entity
            if start:
                entities.append(tag[0])
        if len(entities) > 0:
            firstEntity = reduce(lambda string, entity: '{} {}'.format(string, entity), entities)
        return firstEntity

    def get_lists(self):
        lists = self.webpage.find_all('li')
        featureList = []
        for li in lists:
            featureList.append({
                'listName': li.get_text(),
                'contents': [element for element in li.recursiveChildGenerator()],
                'prevSibling': get_sibling_tag([sib for sib in li.previous_siblings]),
                'nextSibling': get_sibling_tag([sib for sib in li.next_siblings])
            })
        return featureList

    def get_headers(self):
        return self.webpage.find_all('h1') + self.webpage.find_all('h2') + self.webpage.find_all('h3') \
               + self.webpage.find_all('h4') + self.webpage.find_all('h5') + self.webpage.find_all('h6') \
               + self.webpage.find_all('header')

    def _get_labeled_links(self):
        submission = ['submit', 'submission']
        faqs = ['faq', 'f.a.q.', 'frequently asked questions']
        emailPattern = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        linkFeatures = []
        for link in self.webpage.find_all('a'):
            if 'href' in link.attrs:
                prevSibling = get_sibling_tag([sib for sib in link.previous_siblings]),
                nextSibling = get_sibling_tag([sib for sib in link.next_siblings])
                text = link.get_text()
                url = link['href']
                if any(word in text.lower() for word in submission):
                    label = 'submissionDate'
                    url = urljoin(self.url, url)
                elif any(word in text.lower() for word in faqs):
                    label = 'faq'
                    url = urljoin(self.url, url)
                elif emailPattern.match(url):
                    label = 'email'
                    url = format_email(url)
                elif emailPattern.match(text):
                    label = 'email'
                    url = format_email(text)
                else:
                    label = 'unknown'
                linkFeatures.append({
                    'url': url,
                    'text': text,
                    'tag': link,
                    'prevSibling': prevSibling,
                    'nextSibling': nextSibling,
                    'parent': link.parent,
                    'label': label
                })

        return linkFeatures

    def recursive_walk(self):
        if self.webpage.body is None:
            return None

        dateTimeAttrs = []
        locationAttrs = []
        headers = []
        links = []
        dateKeywords = ['time', 'date', 'datetime', 'when']
        locationKeywords = ['conference', 'location', 'place', 'locale', 'venue']
        for child in self.webpage.body.recursiveChildGenerator():
            if type(child) is Tag:
                for attribute in child.attrs:
                    if child.name == 'a':
                        links.append(child)
                    if any(word in attribute for word in dateKeywords):
                        dateTimeAttrs.append(child)
                    if child.name is not None and child.name.startswith('h'):
                        headers.append({'tag': child.name, 'text': child.text})
                    elif any(word in attribute for word in locationKeywords):
                        locationAttrs.append(child)
        return {'dates': dateTimeAttrs, 'locations': locationAttrs, 'links': links, 'headers': headers}

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
            if type(entity) is tuple:
                entity = entity[0]
            context = self._get_context(text, entity).lower()
            if ':' in context:
                context = context[:context.find(':')]
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

    # use regexes to match a set of candidate dates from the input text
    # returns a list of tuples, one tuple per date match
    # tuple contains: (text of date, start pos, end pos)
    def _extract_dates(self, text):
        dates = []
        iters = []

        iters += re.finditer(r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})', text)  # '2-24-6575 and a second one 23/34/6445')

        # add the match to our list of dates
        for match in iters:
            dates .append((match.group(), match.start(), match.end()))

        # dates += re.findall(r"(\w+)\s(\d?\d),?\s?'?(\d{4})", text) #'November 23, 2018')
        potential_matches = []
        potential_matches.append(re.finditer(r"((?:\d{1,2}\s?[‒-]?\s?)?\d{1,2}\s[A-Za-z]+,?\s?'?\d{2,4})", text))  # "23 November 3942 and 3 November '48 and 23 November, 3948")
        # dates += re.findall(r"(\w+)\s(\d{1,2})[trs][tdh]\s?,?\s?(\d{4})?", text)
        potential_matches.append(re.finditer(r"((?:\d{2}\s)?(?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}" +
                        r"(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s(?:\d{4}|\d{1,2})" +
                        r"(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?" +
                        r"(?:\s\d{4}?)?)", text)) # "September 18-20, 2017", "April 15, 2017",

        # add the match to our list of dates if the match contains a month or month abbreviation
        for iterator in potential_matches:
            for match in iterator:
                if any(month.lower() in match.group().lower() for month in months):
                    dates.append((match.group(), match.start(), match.end()))

        return dates

    def _extract_first_email(self, text):
        firstEmail = None
        pattern = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        emails = pattern.findall(text)
        if len(emails) > 0:
            firstEmail = emails[0]

        return firstEmail

def get_sibling_tag(siblings: list):
    sibling = None
    tagSiblings = [sib for sib in siblings if type(sib) is Tag]
    if len(tagSiblings) > 0:
        sibling = tagSiblings[0]
    return sibling


# Find relevant attributes for submissions
def find_relevant_attrs(tag: Tag):
    keywords = ['submit', 'submission']
    for attribute in tag.attrs:
        if any(word in attribute for word in keywords) or \
                any(word in tag.attrs[attribute] for word in keywords):
            relevantAttr = str(tag.attrs[attribute])
            # if str(attribute) == 'href' and is_relative_url(relevantAttr):
            #     relevantAttr = reconstruct_relative_url(relevantAttr)
            print('Found relevant attribute:', relevantAttr)


def has_matching_parent(tag: Tag, pattern):
    curTag = tag.parent
    isMatch = False
    while not isMatch and curTag is not None:
        print('Trying to match:', curTag.string)
        if curTag.string is not None and pattern.match(curTag.string.lower()):
            isMatch = True
            print('Found matching pattern in parent tag')
        curTag = curTag.parent
    return isMatch


def is_relative_url(url: str):
    relativePattern = re.compile(r'^(?!www\.|(?:http|ftp)s?://|[A-Za-z]:\\|//).*')
    isRelative = False
    if relativePattern.match(url):
        isRelative = True
    return isRelative


def label_email_feature(emailFeature):
    if 'parent' not in emailFeature:
        raise KeyError('Invalid emailFeature in label_email_features')

    submissionKeywords = ['submit', 'submission', 'paper', 'abstract']
    if any(word in emailFeature['parent'].get_text().lower() for word in submissionKeywords):
        label = 'submission'
    else:
        label = 'unknown'

    return label, emailFeature['url']


def format_email(email: str):
    if email.startswith('mailto:'):
        email = email[email.find(':') + 1:]
    return email


# Looks for the first <ul>, <li>, or <table> tags in the sibling tags and their children
# Return: list of topics or None if no topics found
def find_list(soup: BeautifulSoup):
    tags = [tag for tag in soup.nextSiblingGenerator() if type(tag) is Tag]
    for tag in tags:
        if tag.name == 'ul' or tag.name == 'ol':
            return [element.string for element in tag.contents if type(element) is Tag]
        elif tag.name == 'table':
            return extract_table_topics(tag)
        else:
            for child in tag.recursiveChildGenerator():
                if type(child) is Tag:
                    if child.name == 'ul' or child.name == 'ol':
                        return [element.string for element in child.contents if type(element) is Tag]
                    elif child.name == 'table':
                        return extract_table_topics(child)
    return None


def extract_table_topics(table: BeautifulSoup):
    print('Extracting topics from a table')
    lists = table.find_all('li')
    if len(lists) > 0:
        topics = [element.string for element in lists]
        print('Found lists of topics:', topics)
    else:
        topics = [column.string for column in table.find_all('td')]
    return topics


# Attempt to find a list of topics inside the text of the target tag
# TODO: Unless this is trivial, don't bother
def find_topics_in_text(tag: Tag):
    pattern = re.compile(r'(topics?)|(subjects?)')
    if tag.string is not None:
        pass
    return None


# Looks for a list-like construction with repeated tags, e.g. repeated <span>, <div>, etc.
def find_list_like_set(soup: BeautifulSoup):
    # print('Trying to find list-like set of tags...')
    siblings = [tag for tag in soup.nextSiblingGenerator() if tag.name != 'br']
    # print('List of siblings:', siblings)
    tagFreqs = [nltk.FreqDist([child.name for child in sib.recursiveChildGenerator() if type(child) is Tag])
                for sib in siblings if type(sib) is Tag]
    # print('TagFreqs:', tagFreqs)
    # for tag in siblings:
    #     if tag.name not in prominentTags:
    #         prominentTags[tag.name] = 0
    #     else:
    #         prominentTags[tag.name] += 1
    # for tagType in prominentTags:
    #     if mostProminentTag[1] < prominentTags[tagType]:
    #         mostProminentTag = tagType, prominentTags[tagType]
    # print('Most prominent tag following topics/subject:', mostProminentTag)


def collapse_entities(named_entities: list, entity_type: str):
    entity_type = entity_type.upper()
    start = False
    entities = []
    curEntity = ''

    for entity in named_entities:
        if start and entity[1] != entity_type:
            if entity_type == 'DATE' and entity_is_years_list(curEntity):
                entities.extend(curEntity.split(' '))
            else:
                entities.append(re.sub(r'\s+,', ',', re.sub(r'\s+', ' ', curEntity.strip())))
            # entities.append(curEntity)
            curEntity = ''

        start = entity[1] == entity_type
        if start:
            curEntity += entity[0] + ' '
            # curEntity += entity[0]

    if curEntity != '':
        print('Appending last entity:', curEntity)
        entities.append(re.sub(r'\s+,', ',', re.sub(r'\s+', ' ', curEntity.strip())))
    return entities


def entity_is_years_list(entity: str):
    is_years = False
    year_pattern = re.compile(r'\d\d\d\d\s+(\d\d\d\d\s+)+')
    if year_pattern.match(entity):
        is_years = True
        print('Entity matches year pattern:', entity)
    return is_years
