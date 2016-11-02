
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
#soup = BeautifulSoup(open('resources/smart_contracts.html'), 'html.parser')
soup = BeautifulSoup(open('resources/history.html'), 'html.parser')

txt = soup.getText()
text = nltk.word_tokenize(txt)
words = [word for word in text if word.lower() not in stopwords.words('english') and word.strip()]
pos = nltk.pos_tag(words)
print(words)


#ner = nltk.ne_chunk(pos)
#print(ner)

st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') 
ner = st.tag(words)
ner = [entity for entity in ner if entity[1] != 'O']
print(ner)

start = False
confLoc = []
for tag in ner:
    if start and tag[1] != 'LOCATION':
        break
    
    start = tag[1] == 'LOCATION'
    
    if start:
        confLoc += tag

organizers = [tag for tag in ner if tag[1] == 'ORGANIZATION']
people = [tag for tag in ner if tag[1] == 'PERSON']

print(confLoc)
print(organizers)
print(people)


Text = nltk.Text(text)
#print(Text.concordance(organizers[0][0]))
#print(Text.concordance(people[0][0], 100))

#kinda meh
#r"(\w+)\s(\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?),?\s(\d{4})?"
#print(re.findall(r"(?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?",

#pretty good
#r"((?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s\d{1,2}(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?)"

#print(re.findall(r"(?:\d{2}\s)?(?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?[A-Za-z]+\s(?:\d{4}|\d{1,2})(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?",
#    '''
#    Tools. A full Reference & Help is available in the Library, or watch the video Tutorial.
#
#    November 23, 2018
#    23 November 3948
#    23 November '48
#    23 November, 3948
#
#
#    June 30th‒July 1st 2017
#    June 30th, 2145
#    February 20-24, 2017
#    February 20th-24th, 2017
#
#    Sample text for testing:
#    '''
#    ))

#use a bunch of awful regexes to get some shitty dates off these sites
def extractDates(text):
    dates = re.findall(r'(\d+/\d+/\d+)', text)#'12/30/1994 and another one 5/23/16')
    dates += re.findall(r'(\d{2})[/.-](\d{2})[/.-](\d{4})', text) #'2-24-6575 and a second one 23/34/6445')
    #dates += re.findall(r"(\w+)\s(\d?\d),?\s?'?(\d{4})", text) #'November 23, 2018') 
    #dates += re.findall(r"\d{1,2}\s[A-Za-z]+,?\s?'?\d{4}", text) #"23 November 3942 and 3 November '48 and 23 November, 3948")
    #dates += re.findall(r"(\w+)\s(\d{1,2})[trs][tdh]\s?,?\s?(\d{4})?", text)
    #ew = re.findall(r"((?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?([A-Za-z]+)\s\d{1,2}(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?)", text)
    ew = re.findall(r"(?:\d{2}\s)?(?:[A-Za-z]+\s\d{1,2}(?:[trs][tdh])?(?:-\d{1,2}(?:[trs][tdh])?)?\s*[‒-]\s*)?[A-Za-z]+\s(?:\d{4}|\d{1,2})(?:[trs][tdh])?(?:\s*-\s*\d{1,2}(?:[trs][tdh])?)?,?(?:\s\d{4}?)?", text)

    print(ew)
    for gross in ew:
        print(gross)
        if gross[1].lower() in months:
            dates.append(gross[0])

    return set(dates)

print(extractDates(txt))
