import React, { Component } from 'react';
import { Card, Row, Col, CardPanel } from 'react-materialize';
import { Collapse } from 'react-bootstrap';

import './styles/CFPResultCard.css';

export default class CFPResultCard extends Component {
  constructor(props) {
    super(props);
    this.state = { areDetailsVisible: false };
    this.onClickDetails = this.onClickDetails.bind(this);
  }

  onClickDetails() {
    this.setState({ areDetailsVisible: !this.state.areDetailsVisible });
  }

  render() {
    let cfp = this.props.cfp;
    let name = cfp != null && cfp.conferenceName != null ? cfp.conferenceName : cfp.url.hostname;
    let location = cfp.location != null ? cfp.location : 'Unknown Location';
    let date;

    if (cfp.startDate != null) {
      let conferenceDate = cfp.conferenceDate != null ? cfp.conferenceDate.format('MMM D YYYY') : 'Unknown Date';
      date = (
        <div className='col-md-3 card-date'>
          <div className='row'>
            <div className='col-md-12 month'>{conferenceDate.format('MMM')}</div>
          </div>
          <div className='row'>
            <div className='col-md-12 day'>{conferenceDate.format('D')}</div>
          </div>
          <div className='row'>
            <div className='col-md-12 year'>{conferenceDate.format('YYYY')}</div>
          </div>
        </div>
      );
    } else {
      date = <div className='col-md-3 card-date'>Unknown</div>;
    }

    return (
      <Col className='result-card' s={12} m={3}>
        <Row className='dark-blue result-card-title'
          onClick={this.onClickDetails}>
          <h3>{location}</h3>
        </Row>
        <Row className='white'>
          <Col m={12}>{name}</Col>
        </Row>
        <Row className='white'>
          <Col m={12}>Submission Date</Col>
        </Row>
        <Row className='white'>
          <Col m={12}>Email</Col>
        </Row>
        <Collapse in={this.state.areDetailsVisible}>
          <div>Blah blah blah</div>
        </Collapse>
      </Col>
    );
  }
}