import json

with open('config.json') as file:
    file = json.loads(file.read())

def get_env():
    return file