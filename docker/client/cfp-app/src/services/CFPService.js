import $ from 'jquery-ajax/jquery';
import CFP from '../models/CFP.js';

const BASE_URL = 'http://localhost:5000/';

export default class CFPService {
  getAllCFPs() {
    let promise = new Promise((resolve, reject) => {
      $.ajax({
        type: 'GET',
        url: BASE_URL + 'get-all-cfps'
      }).done((response) => {
        if (response != null && response.length > 1) {
          response = response.map((cfp) => new CFP(cfp));
        }
        resolve(response);
      });
    });

    return promise;
  }
}
