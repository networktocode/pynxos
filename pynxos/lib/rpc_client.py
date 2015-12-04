import requests
from requests.auth import HTTPBasicAuth
import json

from builtins import range

class RPCClient(object):
    def __init__(self, host, username, password, transport=u'http', port=80):
        self.url = u'%s://%s:%s/ins' % (transport, host, port)
        self.headers = {u'content-type': u'application/json-rpc'}
        self.username = username
        self.password = password

    def _build_payload(self, commands, method, rpc_version=u'2.0'):
        payload_list = []

        id_num = 1
        for command in commands:
            payload = dict(jsonrpc=rpc_version,
                           method=method,
                           params=dict(cmd=command, version=1),
                           id=id_num,)

            payload_list.append(payload)
            id_num += 1

        return payload_list

    def send_request(self, commands, method=u'cli', timeout=30):
        payload_list = self._build_payload(commands, method)
        response = requests.post(self.url,
                                 timeout=timeout,
                                 data=json.dumps(payload_list),
                                 headers=self.headers,
                                 auth=HTTPBasicAuth(self.username, self.password),)

        response_list = json.loads(response.text)

        if isinstance(response_list, dict):
            response_list = [response_list]

        for i in range(len(commands)):
            response_list[i][u'command'] = commands[i]

        return response_list