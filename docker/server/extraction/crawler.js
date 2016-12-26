/**
 * Use for loading any dynamic web pages.
 */

var system = require('system');
var page = require('webpage').create();
var fs = require('fs');

var args = system.args;
var targetUrl, targetLoc;

if (args.length >= 3) {
  targetUrl = args[1];
  targetLoc = args[2];
}
else {
  console.log('Usage: phantomjs Crawler.js <targetURL> <outputLocation>');
  phantom.exit();
}

page.onLoadFinished = function() {
  window.setTimeout(function () {
    console.log('Retrieved page: ' + page.url);

    if (!targetLoc.substring(targetLoc.length - 1) != '/') {
      targetLoc += '/';
    }

    var file = page.title + '.html';

    file = file.replace(/\//, '-');

    fs.write(targetLoc + file, page.content, 'w');
    phantom.exit();
  }, 2000);
};

page.open(targetUrl, function(status) {
  console.log("Status: " + status);
  if(status === "success") {
    page.render('example.png');
  }
});
