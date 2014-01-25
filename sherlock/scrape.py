import dropbox
import json
from db import DBConnector

conn = DBConnector()
users = [x for x in conn.get_all_users()]

for user in users:
    access_token = user['access_token']
    if access_token is None:
        continue
    
    try:
        client = dropbox.client.DropboxClient(access_token)
        client.account_info()
    except dropbox.rest.ErrorResponse, e:
        print 'invalid dropbox access_token'
        continue
    
    delta = client.delta(user['cursor'])
    #conn.update_cursor(user['uid'], delta['cursor'])
    
    for entry in delta['entries']:
        name = entry[0]
        data = entry[1]
        if data['is_dir']:
            continue
        print name
        print data
        # download image
        # parse out EXIF data
        # get lat/long from geo data
        # insert a picture into DB
        # create hash/compare/etc
