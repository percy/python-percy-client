import requests


class Connection(object):
    def __init__(self):
        pass

    def get(self, path, options={}):
        headers = {
          'Content-Type': 'application/vnd.api+json'
        }
        response = requests.get(path, headers=headers)
        # Exception handling TODO
        return response.json()

    def post(self, path, data, options={}):
        response = requests.post(path, data=data)
        return response.json()
