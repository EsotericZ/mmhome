import requests
import json

def GetScales():
    api_url = "http://10.0.1.78:81/Scale/GetScales"
    response = requests.get(api_url)
    return response.json()

def GetSensors():
    api_url = "http://10.0.1.78:81/Scale/GetSensors"
    response = requests.get(api_url)
    return response.json()

def CreateScale(data):
    api_url = "http://10.0.1.78:81/Scale/CreateScale"
    hdr = {"Content-Type": "application/json"}
    test = json.dumps(data.__dict__, indent= 4)
    response = requests.post(api_url, test, headers=hdr)
    return ''

def ZeroScale(data):
    api_url = f"http://10.0.1.78:81/Scale/ZeroScale/{data}"
    response = requests.post(api_url)
    return ''

def CreateItem(data):
    api_url = "http://10.0.1.78:81/Scale/CreateItem"
    hdr = {"Content-Type": "application/json"}
    test = json.dumps(data, indent= 4)
    response = requests.post(api_url, test, headers=hdr)
    return ''

def DeleteScale(data):
    api_url = f"http://10.0.1.78:81/Scale/DeleteScale/{data}"
    response = requests.post(api_url)
    return ''

def DeleteItem(data):
    api_url = f"http://10.0.1.78:81/Scale/DeleteItem/{data}"
    response = requests.post(api_url)
    return ''

def GetLogs():
    api_url = "http://10.0.1.78:81/Scale/GetLogs"
    response = requests.get(api_url)
    return response.json()