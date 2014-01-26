import commands
import re
import dropbox
import pHash
import os
import tempfile
import datetime
import json
import EXIF
from PIL import Image
import StringIO
import dateutil.parser
from db import DBConnector

conn = DBConnector()
highest_group = conn.get_highest_group()
users = [x for x in conn.get_all_users()]

IMAGE_WIDTH = 200

def save_and_resize_image(user_name,file_name,local_name):
    img = Image.open(local_name)
    width, height = img.size
    ratio = float(height)/width
        
    rez = img.resize((IMAGE_WIDTH,(int(IMAGE_WIDTH*ratio))), Image.ANTIALIAS)
    new_file_name = "media/thumbnails/" + str(user_name) + file_name.split("/")[-1]
    rez.save(new_file_name,"JPEG")

    
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
	
	save_and_resize_image(user["_id"],data['path'],temp.name)
	ff = open(temp.name)
        exif_data = EXIF.process_file(ff)
	ff.close()

        if exif_data.get('Image DateTime',None) is not None:
              timestamp = dateutil.parser.parse(exif_data['Image DateTime'].values)
        else:
              timestamp = datetime.datetime(1970,1,1)

        if exif_data.has_key('GPS GPSLongitude') and exif_data.has_key('GPS GPSLatitude'):
            latitude = exif_data['GPS GPSLatitude'].values
            longitude = exif_data['GPS GPSLongitude'].values

            latRef = exif_data['GPS GPSLatitudeRef'].values
            longRef = exif_data['GPS GPSLongitudeRef'].values

            latitude = float(str(latitude[0])) + float(str(latitude[1]))/60
            if latRef == 'S':
                latitude *= -1

            longitude = float(str(longitude[0])) + float(str(longitude[1]))/60
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
        
	is_duplicate = False
        group = 1
	is_unique = True
        for image in images:
            if pHash.hamming_distance(hash1, long(image['hash'])) < 15:
		is_unique = False
            	if image_quality < image['quality']:
                    group = image['group']
		    is_duplicate = True 
		    break
		elif not image['is_duplicate']:
                    group = image['group']
		    conn.mark_image_duplicate(image["_id"])
	            break
	if is_unique:
		highest_group += 1
		group = highest_group	
	conn.insert_image(user["_id"],data["path"],[latitude, longitude],"xx",hash1,timestamp,group,image_quality,is_duplicate=is_duplicate)
        os.unlink(temp.name)
        # download image
        # parse out EXIF data
        # get lat/long from geo data
        # insert a picture into DB
        # create hash/compare/etc
