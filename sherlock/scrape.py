from PIL import Image
import dropbox
import pHash
import os
import tempfile
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
        
        if not data['path'].endsWith('.jpg'):
            continue

        print name
        print data

        
        f, metadata = client.get_file_and_metadata(data['path'])
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(f.read())
        temp.close()
        
        img = Image.open(temp.name)
        exif_data = img._getexif()
        print exif_data
        break
        hash1 = pHash.imagehash(temp.name)

        #image_quality = #

        images = conn.get_image(user_id=user['user_id'], is_duplicate=True)
        for image in images:
            # different shit
            if pHash.hamming_distance(hash1, image['hash']) > 10:
            #    conn.insert_image(# 
            # same shit but worse quality
            #elif image_quality < image['quality']:
            #    conn.insert_image(#
                print 'test'
            else:
                print 'test'
            #    conn.isnert_image(#

        os.unlink(temp.name)
    break
        # download image
        # parse out EXIF data
        # get lat/long from geo data
        # insert a picture into DB
        # create hash/compare/etc
