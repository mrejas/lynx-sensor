import json
import urequests

class Lynx:
    def __init__(self, baseurl, installation, token):
        self.baseurl = baseurl
        self.installation = installation
        self.token = token

    def create_device_if_needed(self, definition):
        # Check if device exists
        headers = {'X-API-Key': self.token.decode('utf-8')}

        url = 'https://' + self.baseurl + '/api/v2/devicex/' + str(self.installation) + '?' + 'mac=' + definition['meta']['mac']  
        response = urequests.get(url, headers=headers)
        res = response.json()
        
        if len(res) == 0:
            print('Will create device ...')
            data = (json.dumps(definition)).encode()
            url = 'https://' + self.baseurl + '/api/v2/devicex/' + str(self.installation)  
            response = urequests.post(url, headers=headers, data=data)
            ret = response.json()
            print('... Done')
        else:
            print('Device exists')
            ret = res[0]

        return(ret['id'])

    def create_function_if_needed(self, definition):
        # Check if device exists
        headers = {'X-API-Key': self.token.decode('utf-8')}

        url = 'https://' + self.baseurl + '/api/v2/functionx/' + str(self.installation) + '?' + 'device_id=' + definition['meta']['device_id'] + '&' + 'topic_read=' + definition['meta']['topic_read']
        response = urequests.get(url, headers=headers)
        res = response.json()
        
        if len(res) == 0:
            print('Will create function ...')
            data = (json.dumps(definition)).encode()
            url = 'https://' + self.baseurl + '/api/v2/functionx/' + str(self.installation)  
            response = urequests.post(url, headers=headers, data=data)
            ret = response.json()
            print('... Done')
        else:
            print('Function exists')
            ret = res[0]

        return(ret['id'])
