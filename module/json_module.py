import json

def open_json(name):
    with open(name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data