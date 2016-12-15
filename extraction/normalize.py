import re
import dateutil.parser as dateParser
import daterangeparser as rangeParser
from datetime import date

# transform a string date or date-range into a datetime
# ex: "Tuesday 29 May -> Sat 2 June 2012"  becomes   (datetime.datetime(2012, 5, 29, 0, 0), datetime.datetime(2012, 6, 2, 0, 0))

year_only_pattern = re.compile(r'^\d\d\d\d$')

MIN_YEAR = 1900
MAX_YEAR = 2100


class CFPDate:
    def __init__(self, date: date, is_year_only=False):
        self._date = date
        self.is_year_only = is_year_only
        self.year = date.year

        if not self.is_year_only:
            self.month = date.month
            self.day = date.day

    def __eq__(self, other):
        if self.is_year_only:
            return False
        else:
            return self._date.__eq__(other)

    def __str__(self):
        if self.is_year_only:
            return str(self.year)
        else:
            return self._date.isoformat()

    def isoformat(self):
        return self.__str__()


def normalizeDate(date: str):
    normalized_date = None

    if date is not None:
        if year_only_pattern.match(date.strip()):
            return None
            # normalized_date = CFPDate(dateParser.parse(date.strip()), is_year_only=True)
        # date = re.sub(r'[]', re.sub(r'\s+', ' ', date))
        # check for and handle date ranges (i.e. June 30th‒July 1st 2017, 12/30 - 12/31/17)
        else:
            try:
                range = rangeParser.parse(date)
                # if date actually isn't a range, return that, otherwise return a range
                if range[1] == None:
                    normalized_date = range[0]
                else:
                    normalized_date = range
            except:
                # print("couldn't parse", date, "as normal range")
                pass

            # if the range parse failed, try to split on hyphen and try manually parse range
            if normalized_date is None and '-' in date:
                try:
                    range = date.split('-')
                    if len(range) == 2:
                        date1, date2 = dateParser.parse(range[0].strip(), fuzzy_with_tokens=True)[0], \
                                       dateParser.parse(range[1].strip(), fuzzy_with_tokens=True)[0]
                        normalized_date = (date1, date2)
                except:
                    # print("couldn't manually parse as range", date)
                    pass

            # otherwise just parse and return the single date
            if normalized_date is None:
                try:
                    normalized_date = dateParser.parse(date, fuzzy_with_tokens=True)[0]
                except Exception:
                    # print("couldn't parse", date, "as single date")
                    pass
            # Fix dates if start and end were somehow reversed
            if normalized_date is not None and type(normalized_date) is tuple and normalized_date[0] > normalized_date[1]:
                new_end, new_start = normalized_date
                normalized_date = (new_start, new_end)

            # Check if the date is garbage or not
            if normalized_date is not None:
                if type(normalized_date) is tuple:
                    start, stop = normalized_date
                    start_year = int(start.year)
                    stop_year = int(stop.year)

                    # Both dates are garbage
                    if (start_year < MIN_YEAR or start_year > MAX_YEAR) and (stop_year < MIN_YEAR or stop_year > MAX_YEAR):
                        print('Garbage start date: start={}'.format(start))
                        normalized_date = None
                    # Start is garbage, but stop is fine
                    elif start_year < MIN_YEAR or start_year > MAX_YEAR:
                        print('Garbage start date: start={}'.format(start))
                        normalized_date = stop
                    # Stop is garbage, but start is fine
                    elif stop_year < MIN_YEAR or stop_year > MAX_YEAR:
                        print('Garbage stop date: stop={}'.format(stop))
                        normalized_date = start
                elif int(normalized_date.year) < MIN_YEAR or int(normalized_date.year) > MAX_YEAR:
                    print('Garbage date:', normalized_date)
                    normalized_date = None

    # print("Couldn't parse date:", date)
    # if normalized_date is not None and type(normalized_date) is tuple:
    #     date_one, date_two = normalized_date
    #     print('NormalizedDate range={} to {}, original={}'.format(
    #         date_one.isoformat(), date_two.isoformat(), date))
    # elif normalized_date is not None:
    #     print('NormalizedDate={}, original={}'.format(normalized_date.isoformat(), date))
    # else:
    #     print('NormalizedDate=None, original={}'.format(date))
    return normalized_date

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
