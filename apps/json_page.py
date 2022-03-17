import dash_bootstrap_components as dbc
from flask import request
from app import app


@app.server.route('/json', methods=['GET'])
def retrieve_data():
    if request.method == 'GET':
        print(request.json)
        count = len(request.json['links'])
        return {'Count': f'{count}'}
    else:
        print('Failed')
        return {'':''}

