import dropbox
import json
from db import DBConnector


conn = DBConnector()
stuff = conn.add_user('19241364', 'safety first')
print stuff

"""
access_token = 'safety first'
client = dropbox.client.DropboxClient(access_token)
deltas = client.delta()
print json.dumps(deltas, sort_keys=True,
               indent=4, separators=(',', ': '))
cursor = deltas['cursor']
for entry in deltas['entries']:
    name = entry[0]
    data = entry[1]
    if data['is_dir']:
        continue
    print name + "\n"
    """
