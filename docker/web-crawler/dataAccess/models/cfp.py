ID = '_id'
URL = 'url'
PEOPLE = 'people'
LOCATION = 'location'
CONFERENCE_START = 'conference_start'
CONFERENCE_END = 'conference_end'
CONFERENCE_NAME = 'conference_name'
TOPICS = 'topics'
EMAIL = 'email'
SUBMISSION_DATE = 'submission_date'
SUBMISSION_LINK = 'submission_link'
IMPORTANT_LINKS = 'important_links'


class CFP:
    def __init__(self, cfp: dict = None):
        # self._labeled_site = labeled_site
            if cfp is not None and ID in cfp:
                self._id = cfp[ID]
            if cfp is not None and URL in cfp:
                self._url = cfp[URL]
            else:
                self._url = None
            if cfp is not None and PEOPLE in cfp:
                self._people = cfp[PEOPLE]
            else:
                self._people = None
            if cfp is not None and LOCATION in cfp:
                self._location = cfp[LOCATION]
            else:
                self._location = None
            if cfp is not None and CONFERENCE_START in cfp:
                self._conference_start = cfp[CONFERENCE_START]
            else:
                self._conference_start = None
            if cfp is not None and CONFERENCE_END in cfp:
                self._conference_end = cfp[CONFERENCE_END]
            else:
                self._conference_end = None
            if cfp is not None and CONFERENCE_NAME in cfp:
                self._conference_name = cfp[CONFERENCE_NAME]
            else:
                self._conference_name = None
            if cfp is not None and TOPICS in cfp:
                self._topics = cfp[TOPICS]
            else:
                self._topics = None
            if cfp is not None and EMAIL in cfp:
                self._email = cfp[EMAIL]
            else:
                self._email = None
            if cfp is not None and SUBMISSION_DATE in cfp:
                self._submission_date = cfp[SUBMISSION_DATE]
            else:
                self._submission_date = None
            if cfp is not None and SUBMISSION_LINK in cfp:
                self._submission_link = cfp[SUBMISSION_LINK]
            else:
                self._submission_link = None
            if cfp is not None and IMPORTANT_LINKS in cfp:
                self._important_links = cfp[IMPORTANT_LINKS]
            else:
                self._important_links = None
                # self._dates = None
                # self._conference = None
                # self._topics = None
                # self._email = None
                # self._submissionLink = None
                # self._importantLinks = []
                # self.isValidDocument = False
                # if html is not None:
                #     self.webpage = BeautifulSoup(html, 'html.parser')
                #
                #     if self.webpage.body is not None:
                #         self.isValidDocument = True
                #     else:
                #         self.isValidDocument = False

    def __str__(self):
        return '<CFP:\n_id={}\ntopics=[{}]\nlocation={}\nconferenceDate={}' \
               '\nconferenceName={}\nemail={}\nsubmissionLink={}\nimportantLinks={}>'.format(
            self.id, self.topics, self.location, self.conference_start, self.conference_name,
            self.email, self.submission_link, self.important_links
        )

    def serialize(self):
        serialized = {}
        serialized[ID] = str(self._id)
        serialized[URL] = self._url
        serialized[PEOPLE] = self._people
        serialized[LOCATION] = self._location
        serialized[CONFERENCE_START] = self._conference_start
        serialized[CONFERENCE_END] = self._conference_end
        serialized[CONFERENCE_NAME] = self._conference_name
        serialized[TOPICS] = self._topics
        serialized[EMAIL] = self._email
        serialized[SUBMISSION_DATE] = self._submission_date
        serialized[SUBMISSION_LINK] = self._submission_link
        serialized[IMPORTANT_LINKS] = self._important_links

        return serialized

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def people(self):
        return self._people

    @people.setter
    def people(self, value):
        self._people = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def conference_start(self):
        return self._conference_start

    @conference_start.setter
    def conference_start(self, value):
        self._conference_start = value

    @property
    def conference_end(self):
        return self._conference_end

    @conference_end.setter
    def conference_end(self, value):
        self._conference_end = value

    @property
    def conference_name(self):
        return self._conference_name

    @conference_name.setter
    def conference_name(self, value):
        self._conference_name = value

    @property
    def topics(self):
        return self._topics

    @topics.setter
    def topics(self, value):
        self._topics = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def submission_date(self):
        return self._submission_date

    @submission_date.setter
    def submission_date(self, value):
        self._submission_date = value

    @property
    def submission_link(self):
        return self._submission_link

    @submission_link.setter
    def submission_link(self, value):
        self._submission_link = value

    @property
    def important_links(self):
        return self._important_links

    @important_links.setter
    def important_links(self, value):
        self._important_links = value
