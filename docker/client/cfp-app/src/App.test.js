import React from 'react';
import ReactDOM from 'react-dom';
import CFPSearch from './CFPSearch';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<CFPSearch />, div);
});
