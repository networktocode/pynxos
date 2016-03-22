import os
import json

CURRNENT_DIR = os.path.dirname(os.path.realpath(__file__))

def send_request(commands, method='cli', timeout=30.0):
    if method == 'cli':
        folder = 'send_request'
    elif method == 'cli_ascii':
        folder = 'send_request_raw'

    filename = '__'.join(commands).replace(' ', '_').replace('/', '_')
    filepath = os.path.join(CURRNENT_DIR, folder, filename + '.json')

    with open(filepath, 'r') as f:
        content = json.load(f)

    return content