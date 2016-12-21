import React, { Component } from 'react';
import moment from 'moment/moment.js';
import $ from 'jquery-ajax/jquery';
//import logo from './logo.svg';
import CFP from './models/CFP.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

class CFPSearch extends Component {
  constructor() {
    super();
    this.state = {
      cfpResults: []
    };
    this.search = this.search.bind(this);
  }

  search(query) {
    let results = getCFP(query).then((response) => {
      let resultList = response.map((cfpResponse, index) => {
        let cfp = new CFP(cfpResponse);
        return (
          <tr key={cfp.id}>
            <td><a href={cfp.url}>{cfp.conferenceName}</a></td>
            <td>{cfp.conferenceDate.format('YYYY-MM-DD')}</td>
          </tr>
        );
      });

      this.setState({cfpResults: resultList});
    }).catch((error) => {
      // console.error(error);
      return error;
    });
  }

  render() {
    let resultsTable;
    let cfpResults = this.state.cfpResults.slice();

    if (cfpResults.length > 0) {
      resultsTable = (
        <table className="table">
          <thead className="thead-default">
            <tr>
              <th>Conference Name</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>{cfpResults}</tbody>
        </table>
      );
    }

    return (
      <div className="container">
        <div className="jumbotron">
          <h1 className="h1">Auto Call for Papers</h1>
          <p>A work in progress to automatically retrieve call for papers from conference websites</p>
        </div>
        <div>
          <SearchForm onSubmit={this.search}/>
        </div>
        <div className="results-table">
          {resultsTable}
        </div>
      </div>
    );
  }
}

function getCFP(url) {
  let promise = new Promise((resolve, reject) => {
    $.ajax({
      type: 'GET',
      url:'http://localhost:5000/get-cfp',
      data: {url: url}
    }).done((response) => {
      resolve(response);
    });
  });

  return promise;
}

class SearchForm extends Component {
  constructor(props) {
    super(props);
    this.state = {value: ''};
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    this.props.onSubmit(this.state.value);
    event.preventDefault();
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <div className="form-group">
          <input type="text" className="form-control"
            placeholder="Search"
            value={this.state.value} onChange={this.handleChange} />
          <button className="btn btn-primary" type="submit" value="Submit">Search</button>
        </div>
      </form>
    );
  }
}

export default CFPSearch;