import os
import json
import requests

url = os.getenv('GAS_PROJECT_URL')+'?'

#DBへのPOST処理
async def post_db(param, data):
    uurl = url + f'param={param}'
    output = requests.post(uurl, data=json.dumps(data))
    return output

#DBへのGET処理
async def get_db(param, table, subjectID):
    payload = {'param': param, 'table': table, 'subjectID': subjectID}
    output = requests.get(url, params=payload)
    return output