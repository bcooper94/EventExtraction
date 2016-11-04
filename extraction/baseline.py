
import nltk
import re
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from nltk.tag import StanfordNERTagger

months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec']

#soup = BeautifulSoup(open('cfp/Trusted Smart Contracts 2017.html'), 'html.parser')
#soup = BeautifulSoup(open('cfp/Corpus Historicus – The Body in_of History.html'), 'html.parser')
#soup = BeautifulSoup(open('cfp/Call For Papers – ERA Track _ SANER 2017.html'), 'html.parser')
#soup = BeautifulSoup(open('resources/era_track.html'), 'html.parser')
# soup = BeautifulSoup(open('resources/smart_contracts.html'), 'html.parser')
soup = BeautifulSoup(open('resources/history.html'), 'html.parser')
soup = BeautifulSoup(open('resources/embedded.html'), 'html.parser')

txt = soup.getText()
text = nltk.word_tokenize(txt)
# words = [word for word in text if word.lower() not in stopwords.words('english') and word.strip()]
# pos = nltk.pos_tag(words)
# print(words)


#ner = nltk.ne_chunk(pos)
#print(ner)

st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') 
# ner = st.tag(words)
ner = st.tag(text)
print(ner)
ner = [entity for entity in ner if entity[1] != 'O']
print(ner)

def extract_first_entity(ner, entity):
    start = False
    entities = []

    for tag in ner:
        if start and tag[1] != entity:
            break

        start = tag[1] == entity

        if start:
            entities += tag
    return entities

organizations = [tag for tag in ner if tag[1] == 'ORGANIZATION']
people = [tag for tag in ner if tag[1] == 'PERSON']

print(extract_first_entity(ner, 'LOCATION'))
print(organizations)
print(people)


def label_entities(text, entities, entity_labels):
    labeled_entities = []

    for entity in entities:
        print(entity)
        context = get_context(text, entity).lower()
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

#get's the context surrounding an input phrase
#had to make this because nltk is stupid and doesn't support phrases when context searching
def get_context(text, phrase, range=30):
    beg = text.find(phrase)
    beg = beg if beg - range > 0 else 0
    end = beg + len(phrase)
    end = end if range + end < len(text) else len(text)

    return text[beg - range : end + range]

#use a bunch of awful regexes to recognize some shitty dates off these damn sites
def extract_dates(text):
    dates = re.findall(r'(\d+/\d+/\d+)', text)#'12/30/1994 and another one 5/23/16')
    dates += re.findall(r'(\d{2})[/.-](\d{2})[/.-](\d{4})', text) #'2-24-6575 and a second one 23/34/6445')
    #dates += re.findall(r"(\w+)\s(\d?\d),?\s?'?(\d{4})", text) #'November 23, 2018')
    dates += re.findall(r"\d{1,2}\s[A-Za-z]+,?\s?'?\d{4}", text) #"23 November 3942 and 3 November '48 and 23 November, 3948")
    #dates += re.findall(r"(\w+)\s(\d{1,2})[trs][tdh]\s?,?\s?(\d{4})?", text)
    #ew = re.findall(r"((?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s\d{1,2}(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?)", text)
    ew = re.findall(r"((?:\d{2}\s)?(?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s(?:\d{4}|\d{1,2})(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?)", text)

    # regex isn't perfect, so it only keeps dates with words that are months
    for gross in ew:
        if gross[1].lower() in months:
            bool = False
            for date in dates:
                bool = bool or gross[0] in date
            if not bool:
                dates.append(gross[0])

    return set(dates)




Text = nltk.Text(text)
conference = ['conference', 'association']

abstractDate = ['abstract', 'summary', 'proposal']
paperDate = ['paper', 'final']
conferenceDate = ['conference', 'event', 'time', 'held']
host = ['host']

dates = extract_dates(txt)


print('CONFERENCE')
print(extract_first_entity(ner, 'ORGANIZATION'))
#print(label_entities(txt, organizations))

print('LOCATION')
print(print(extract_first_entity(ner, 'LOCATION')))

print('DATES')
if len(dates) == 1:
    print((list(dates)[0], 'conference'))
else:
    print(label_entities(txt, extract_dates(txt), [abstractDate, paperDate, conferenceDate]))
    # for date in dates:
    #     print(get_context(txt, date, 20))



