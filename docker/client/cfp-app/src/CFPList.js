import React, { Component } from 'react';
import LazyLoad from 'react-lazyload';
import CFPResultCard from './CFPResultCard';
// import ReactList from 'react-list';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'font-awesome/css/font-awesome.css';
import './styles/overwrite.css';
import './styles/style.css';
import './styles/index.css';
import './styles/CFPList.css';

export default class CFPList extends Component {
  render() {
    console.debug('CFPList render: ' + JSON.stringify(this.props.displayedCfps.map(cfp => cfp.url.href)));
    let displayedCfps = this.props.displayedCfps.map((cfp) => (
      <LazyLoad height={136} offset={100} key={cfp._id}>
        <CFPResultCard cfp={cfp} onClickDetails={this.props.onClickDetails} />
      </LazyLoad>
    ));

    return (<div className="container">{displayedCfps}</div>);
  }
}
