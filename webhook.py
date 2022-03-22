import requests
import json

from helpers import db_writer_json

def post_data():
    url = 'http://192.168.2.12:5678/json'

    data = {'links': [
        {'href': 'https://dps.report/getJson?permalink=mJPQ-20220317-212153_wvw'},
        {'href': 'https://dps.report/getJson?permalink=1wYH-20220317-211912_wvw'},
        {'href': 'https://dps.report/getJson?permalink=4gx1-20220317-212555_wvw'},
        {'href': 'https://dps.report/getJson?permalink=7Fec-20220317-212029_wvw'},
        {'href': 'https://dps.report/getJson?permalink=FKAs-20220302-111544_wvw'},
        {'href': 'https://dps.report/getJson?permalink=pqOG-20220317-211958_wvw'},
    ]}

    r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
    
    print(r.json())

    with open('output.json', 'w') as file:
        file.write(json.dumps(r.json()))



def send_json_to_writer():
    with open('output.json', 'r') as file:
        db_writer_json.write_xls_to_db(json.load(file))


#post_data()
send_json_to_writer()
