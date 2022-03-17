import requests
import json


def post_data():
    url = 'http://192.168.2.12:5678/json'

    data = {'links': [
        {'href': 'https://wvw.report/HtYT-20220302-111544_wvw'},
        #{'href': 'https://dps.report/getJson?permalink=FKAs-20220302-111544_wvw'}
    ]}

    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
    
    print(r.json())


post_data()

