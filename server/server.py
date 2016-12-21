from flask import Flask, Response, request, jsonify
import json
import requests
import os

app = Flask(__name__)

all_cfps = [{
    'id': 1,
    'url': 'http://www.google.com/',
    'conferenceName': 'Google Conference',
    'conferenceDate': '2017-01-02'
}, {
    'id': 2,
    'url': 'http://www.msn.com/',
    'conferenceName': 'MSN Conference',
    'conferenceDate': '2017-05-14'
}]


@app.route('/get-cfp', methods=['GET'])
def get_cfp():
    url = request.args.get('url')

    if url is not None:
        print('URL={}'.format(url))
        filtered_cfps = list(filter(lambda cfp: url in cfp['url'], all_cfps))
        print('Filtered:', filtered_cfps)
        response = json_response(filtered_cfps, 200)
    else:
        print('No URL arg')
        response = json_response({'error': 'Missing URL argument'}, 404)

    return(response)


def json_response(data, status):
    response = jsonify(data)
    response.status_code = 200
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
