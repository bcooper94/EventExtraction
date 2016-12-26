from flask import Flask, request, jsonify

from dataAccess.cfps import CFPClient

app = Flask(__name__)

@app.route('/search-cfps', methods=['GET'])
def search_cfps():
    print('Searching CFPs...')
    query = request.args.get('query')

    if query is not None:
        print('URL={}'.format(query))
        results = list(CFPClient().search_cfps(query))
        print('Filtered:', results)
        response = json_response(results, 200)
    else:
        print('No URL arg')
        response = json_response({'error': 'Missing URL argument'}, 404)

    return response


def json_response(data, status):
    response = jsonify(data)
    response.status_code = status
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
