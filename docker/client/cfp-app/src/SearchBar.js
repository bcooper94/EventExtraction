import React, { Component } from 'react';

export default class SearchBar extends Component {
  render() {
    return (
      <div className="container search-container">
        <div className="col-lg-12">
          <div className="form-horizontal">
            <div className="text-center">
              <div className="subscribe">
                  <input type="text" name="search" autoFocus
                    id="email_field" className="faded search_form"
                    placeholder={this.props.searchPlaceholder}
                    onChange={this.props.onInputChange} />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
