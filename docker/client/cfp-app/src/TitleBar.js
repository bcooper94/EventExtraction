import React, { Component } from 'react';

export default class TitleBar extends Component {
  render() {
    return (
      <div className="title">
        <div className="container">
          <div className="col-lg-12 welcome">
            <h1>Auto Call for Papers</h1>
            <p>A place to find all of your conference calls for papers.</p>
          </div>
        </div>
      </div>
    );
  }
}
