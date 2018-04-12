import React, { Component, Fragment } from 'react';
import TitleBar from './TitleBar';
import CFPBrowse from './CFPBrowse';
import CFPDetails from './CFPDetails';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'font-awesome/css/font-awesome.css';
import './styles/overwrite.css';
import './styles/style.css';
import './styles/index.css';


export default class CFPHome extends Component {
  constructor() {
    super();
    this.state = {
      activeWidget: CFPBrowse,
      selectedCfp: null
    };
  }

  showCfpDetails(cfp) {
    console.debug('CFPHome showCfpDetails called on ' + JSON.stringify(cfp));
    this.setState({activeWidget: CFPDetails, selectedCfp: cfp});
  }

  hideCfpDetails() {
    console.debug('CFPHome hiding CFP Details');
    this.setState({activeWidget: CFPBrowse, selectedCfp: null});
  }

  render() {
    let activeWidget;

    switch (this.state.activeWidget) {
      case CFPDetails:
        activeWidget = <CFPDetails cfp={this.state.selectedCfp} onClickBack={this.hideCfpDetails.bind(this)} />
        break;
      case CFPBrowse:
      default:
        activeWidget = <CFPBrowse onClickDetails={this.showCfpDetails.bind(this)} />
    }

    return (
      <Fragment>
        <TitleBar/>
        {activeWidget}
      </Fragment>
    );
  }
}
