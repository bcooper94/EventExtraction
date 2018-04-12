import React, { Component } from 'react';

export default class CFPResultCard extends Component {
  constructor(props) {
    super(props);
    this.onClickDetails = this.onClickDetails.bind(this);
  }

  onClickDetails() {
    this.props.onClickDetails(this.props.cfp);
  }

  render() {
    let cfp = this.props.cfp;
    let name = cfp != null && cfp.conferenceName != null ? cfp.conferenceName : cfp.url.hostname;
    let location = cfp.location != null ? cfp.location : 'Unknown Location';
    let date;

    if (cfp.startDate != null) {
      let conferenceDate = cfp.conferenceDate != null ? cfp.conferenceDate.format('MMM D YYYY') : 'Unknown Date';
      date = (
        <div className="col-md-3 card-date">
          <div className="row">
            <div className="col-md-12 month">{conferenceDate.format('MMM')}</div>
          </div>
          <div className="row">
            <div className="col-md-12 day">{conferenceDate.format('D')}</div>
          </div>
          <div className="row">
            <div className="col-md-12 year">{conferenceDate.format('YYYY')}</div>
          </div>
        </div>
      );
    } else {
      date = <div className="col-md-3 card-date">Unknown</div>;
    }

    return (
      <div className="container-fluid location-card">
        <div className="row">
          <div className="col-md-8 card-location">
            <i className="fa fa-lg fa-map-marker"></i> {location}
          </div>
          <div className="col-md-4 card-button-bar">
            <a href="#"><i className="fa fa-lg fa-edit" onClick={this.onClickDetails}></i></a>
          </div>
        </div>
        <div className="row">
          {date}
          <div className="col-md-9">
            <div className="row">
              <div className="col-md-12">{name}</div>
            </div>
            <div className="row">
              <div className="col-md-12">Submission Date</div>
            </div>
            <div className="row">
              <div className="col-md-12">Email</div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}