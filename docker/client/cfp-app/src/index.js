import React from 'react';
import ReactDOM from 'react-dom';
// import CFPSearch from './CFPSearch';
import CFPHome from './CFPHome';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'font-awesome/css/font-awesome.css';
import './styles/overwrite.css';
import './styles/style.css';
import './styles/index.css';

ReactDOM.render(
  <CFPHome />,
  document.getElementById('root')
);
