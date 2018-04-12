import React, { Component, Fragment } from 'react';
import SearchBar from './SearchBar';
import CFPService from './services/CFPService';
import CFPList from './CFPList';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'font-awesome/css/font-awesome.css';
import './styles/overwrite.css';
import './styles/style.css';
import './styles/index.css';

export default class CFPBrowse extends Component {
  constructor(props) {
    super(props);
    this.state = {
      results: [],
      filteredCfps: []
    };

    let cfpService = new CFPService();
    cfpService.getAllCFPs().then((results) => {
      this.setState({
        results: results,
        filteredCfps: [...results]
      });
    });
  }

  handleSearchChange(event) {
    event.preventDefault();
    let filter = event.target.value != null ? event.target.value.toLowerCase() : '';
    let filteredCfps = this.state.results.filter(cfp =>
      (cfp.url != null && cfp.url.href.toLowerCase().includes(filter)) ||
      (cfp.conferenceName != null &&
        cfp.conferenceName.toLowerCase().includes(filter)) ||
      (cfp.location != null && cfp.location.toLowerCase().includes(filter)));
    this.setState({filteredCfps});
  }

  render() {
    return (
      <Fragment>
        <SearchBar searchPlaceholder="Search call for papers..."
          onInputChange={this.handleSearchChange.bind(this)} />
        <div className="container">
          <CFPList displayedCfps={this.state.filteredCfps}
            onClickDetails={this.props.onClickDetails} />
        </div>
      </Fragment>
    );
  }
}
