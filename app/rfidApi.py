import requests
import json

def GetRFID():
    api_url = 'http://10.0.1.45:3001/logs/getAllLogs'
    response = requests.get(api_url)
    return response.json()['data'][0]['name']
