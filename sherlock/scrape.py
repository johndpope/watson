import commands
import re
import dropbox
import pHash
import os
import tempfile
import datetime
import json
import EXIF
import dateutil.parser
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
        
        if not data['path'].endswith('.jpg'):
            continue


        f, metadata = client.get_file_and_metadata(data['path'])
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(f.read())
        temp.close()

	ff = open(temp.name)
        exif_data = EXIF.process_file(ff)
	ff.close()

        if exif_data.get('Image DateTime',None) is not None:
              timestamp = dateutil.parser.parse(exif_data['Image DateTime'].values)
        else:
              timestamp = datetime.datetime.today()

        if exif_data.has_key('GPS GPSLongitude') and exif_data.has_key('GPS GPSLatitude'):
            latitude = exif_data['GPS GPSLatitude']
            longitude = exif_data['GPS GPSLongitude']

            latRef = exif_data['GPS GPSLatitudeRef'].values
            longRef = exif_data['GPS GPSLongitudeRef'].values

            latitude = latitude[0] + latitude[1]/60
            if latRef == 'S':
                latitude *= -1

            longitude = longitude[0] + longitude[1]/60
            if longRef == 'W':
                longitude *= -1

        else:
            latitude = 0
            longitude = 0

        hash1 = pHash.imagehash(temp.name)
	
        command = 'blur-detection ' + temp.name
        output = commands.getoutput(command)
        p=re.compile('.*density: (\d+\.\d+)')

        image_quality = float(p.match(output).group(1))

        images = conn.get_images(user_id=user['_id'], is_duplicate=False)
        
        # conn.insert_image(
        for image in images:
            # different shit
            if pHash.hamming_distance(hash1, image['hash']) > 10:
                print hash1
            #    conn.insert_image(# 
            # same shit but worse quality
            elif image_quality < image['quality']:
            #    conn.insert_image(#
                print 'test1'
            else:
                print 'test2'
            #    conn.isnert_image(#

        os.unlink(temp.name)
        # download image
        # parse out EXIF data
        # get lat/long from geo data
        # insert a picture into DB
        # create hash/compare/etc
