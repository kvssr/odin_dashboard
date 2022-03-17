import requests
import json


def post_data():
    url = 'http://localhost:8050/json'

    data = {'links': {
        'one': 'onasdoasd',
        'two': 'asdasasddasd'
    }}

    r = requests.get(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
    
    print(r.json())


post_data()

