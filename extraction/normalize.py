import re
import dateutil.parser as dateParser
import daterangeparser as rangeParser

#transform a string date or date-range into a datetime
#ex: "Tuesday 29 May -> Sat 2 June 2012"  becomes   (datetime.datetime(2012, 5, 29, 0, 0), datetime.datetime(2012, 6, 2, 0, 0))
def normalizeDate(date: str):
    if date is None:
        return None
    # date = re.sub(r'[]', re.sub(r'\s+', ' ', date))
    # check for and handle date ranges (i.e. June 30th‒July 1st 2017, 12/30 - 12/31/17)
    try:
        range = rangeParser.parse(date)
        #if date actually isn't a range, return that, otherwise return a range
        if range[1] == None:
            return range[0]
        else:
            return range
    except :
        # print("couldn't parse", date, "as normal range")
        pass

    #if the range parse failed, try to split on hyphen and try manually parse range
    if '-' in date:
        try:
            range = date.split('-')
            if len(range) == 2:
                date1,date2 = dateParser.parse(range[0].strip(), fuzzy_with_tokens=True)[0], \
                              dateParser.parse(range[1].strip(), fuzzy_with_tokens=True)[0]
                return (date1, date2)
        except :
            # print("couldn't manually parse as range", date)
            pass

    # otherwise just parse and return the single date
    try:
        return dateParser.parse(date, fuzzy_with_tokens=True)[0]
    except Exception:
        # print("couldn't parse", date, "as single date")
        pass

    # print("Couldn't parse date:", date)
    return None

# February 20-24, 2017
# June 30th‒July 1st 2017
# June 30th 2017‒July 1st 2017
# 12/30 - 12/31/17




# print(normalizeDate('Tuesday 29 May -> Sat 2 June 2012'))
# print(normalizeDate('29th March 1999'))
#
# print(normalizeDate('February 20-24, 2017'))
# print(normalizeDate('01-Jan-1995'))
# print(normalizeDate('June 30th-July 1st 2017'))
# print(normalizeDate('June 30th 2017-July 1st 2017'))
# print(normalizeDate('12/30 - 12/31/17'))
# print(normalizeDate('12/30/17 - 12/31/17'))
# print(normalizeDate('20 to 21 July 2017'))
