class CFP {
  constructor(cfp) {
    if (cfp == null) {
      return;
    }

    if (cfp.hasOwnProperty('_id')) {
      this._id = cfp._id;
    }
    if (cfp.hasOwnProperty('url')) {
      this.url = cfp.url;
    }
    if (cfp.hasOwnProperty('conference_name')) {
      this.conferenceName = cfp.conference_name;
    }
    if (cfp.hasOwnProperty('conference_date')) {
      this.conferenceDate = cfp.conference_date;
    }
    if (cfp.hasOwnProperty('location')) {
      this.location = cfp.location;
    }
    if (cfp.hasOwnProperty('submission_date')) {
      this.submissionDate = cfp.submission_date;
    }
    if (cfp.hasOwnProperty('topics')) {
      this.topics = cfp.topics;
    }
    else {
      this.topics = [];
    }
    if (cfp.hasOwnProperty('email')) {
      this.email = cfp.email;
    }
    if (cfp.hasOwnProperty('submission_link')) {
      this.submissionLink = cfp.submission_link;
    }
    if (cfp.hasOwnProperty('people')) {
      this.people = cfp.people;
    }
    else {
      this.people = [];
    }
  }

  addTopic(topic) {
    this.topics.push(topic);
  }
}

module.exports = CFP;
