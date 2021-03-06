import moment from 'moment/moment.js';

class CFP {
  constructor(cfp) {
    if (cfp == null) {
      return;
    }

    if (cfp.hasOwnProperty('_id')) {
      this._id = cfp._id;
    }
    if (cfp.hasOwnProperty('url')) {
      this.url = new URL(cfp.url);
    }
    if (cfp.hasOwnProperty('conferenceName')) {
      this.conferenceName = cfp.conferenceName;
    }
    if (cfp.hasOwnProperty('conferenceDate')) {
      this.conferenceDate = moment(cfp.conferenceDate);

      console.debug(this.conferenceDate);
    }
    if (cfp.hasOwnProperty('location')) {
      this.location = cfp.location;
    }
    if (cfp.hasOwnProperty('submissionDate')) {
      this.submissionDate = moment(cfp.submissionDate);
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
    if (cfp.hasOwnProperty('submissionLink')) {
      this.submissionLink = cfp.submissionLink;
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

export default CFP;
