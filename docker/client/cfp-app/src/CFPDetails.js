import React, { Component, Fragment } from 'react';
import moment from 'moment/moment.js';
//import logo from './logo.svg';
// import CFP from './models/CFP.js';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'font-awesome/css/font-awesome.css';
import './styles/overwrite.css';
import './styles/style.css';
import './styles/index.css';


export default class CFPDetails extends Component {
  formatLongDate(date) {
    return moment(date).format('MMMM Do YYYY');
  }

  render() {
    return (
      <Fragment>
        <form>
          <div className="form-group">
            <label htmlFor="cfp-details-location">Location</label>
            <div id="cfp-details-location" className="form-text">{this.props.cfp.location}</div>
          </div>
          <div className="form-group">
            <label htmlFor="cfp-details-start">Conference Start Date</label>
            <div id="cfp-details-start" className="form-text">{this.formatLongDate(this.props.cfp.conferenceStart)}</div>
          </div>
          <div className="form-group">
            <label htmlFor="cfp-details-end">Conference End Date</label>
            <div id="cfp-details-end" className="form-text">{this.formatLongDate(this.props.cfp.conferenceEnd)}</div>
          </div>
          <div className="form-group">
            <label htmlFor="cfp-details-submission-date">Paper Submission Date</label>
            <div id="cfp-details-submission-date" className="form-text">{this.formatLongDate(this.props.cfp.submissionDate)}</div>
          </div>
        </form>
        <button className="btn btn-primary" onClick={this.props.onClickBack}>Back</button>
      </Fragment>
    );
  }
}
