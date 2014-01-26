from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from dropbox.client import DropboxOAuth2Flow, DropboxClient
from django.views.generic import TemplateView
from db import DBConnector
import dropbox
import json
import time
import urllib2
import base64
from bson import json_util
import re
from geopy import geocoders
from datetime import datetime

APP_KEY = 'nice try'
APP_SECRET = 'not happening'

conn = DBConnector()

def get_dropbox_auth_flow(web_app_session):
    redirect_uri = "https://watson.codef.in/auth_finish"
    return DropboxOAuth2Flow(APP_KEY, APP_SECRET, redirect_uri,
        web_app_session, "dropbox-auth-csrf-token")

def auth(request):
    if 'user_id' in request.session:
        print request.session['user_id']
        return index(request)
    return redirect(get_dropbox_auth_flow(request.session).start())

def index(request):
    user = conn.get_user(request.session['user_id'])
    client = dropbox.client.DropboxClient(user['access_token'])
    info = client.account_info()
    print 'user', user['_id']
    print info
    return render_to_response('index.html', {"user": info, "uid": user['_id']})

def search(request):
    user_id = request.session['user_id']
    user = conn.get_user(user_id)
    user_id = user['_id']
    query = request.REQUEST['query']
    	
    matches = re.search('near (.*)', query)
    lat = None
    lng = None
    if matches is not None:
	gh = geocoders.GeoNames(username="watsonht")
	location_string = matches.group(1)
	location = gh.geocode(location_string)
	lat = location[1][0]
	lng = location[1][1]
    
    matches = re.search('last weekend', query)
    starttime = None
    endtime = None
    if query == 'last weekend':
	starttime = datetime(2014, 1, 17)
	endtime = datetime(2014, 1, 20)
	
    images = [x for x in conn.get_images_detailed(user_id, start_time=starttime, end_time=endtime, coords=[lat,lng])]
    return HttpResponse(json.dumps(images, default=json_util.default), content_type="application/json")


def get_image(request):
    print request
    path = request.REQUEST['path']
    user_id = request.session['user_id']
    user = conn.get_user(user_id)
    client = dropbox.client.DropboxClient(user['access_token'])
    try:
        file = client.get_file(path).read()
    except Exception, e:
        file = ''
    return HttpResponse(file, content_type="image/jpeg")

def dropbox_auth_finish(request):
    try:
        access_token, user_id, url_state = \
            get_dropbox_auth_flow(request.session).finish(request.GET)

        conn = DBConnector()
        conn.add_user(user_id, access_token)

        request.session['user_id'] = user_id
        return render_to_response('index.html')
    except DropboxOAuth2Flow.BadRequestException, e:
        http_status(400)
    except DropboxOAuth2Flow.BadStateException, e:
        # Start the auth flow again.
        redirect_to("/dropbox-auth-start")
    except DropboxOAuth2Flow.CsrfException, e:
        http_status(403)
    except DropboxOAuth2Flow.NotApprovedException, e:
        flash('Not approved?  Why not?')
        return redirect_to("/home")
    except DropboxOAuth2Flow.ProviderException, e:
        logger.log("Auth error: %s" % (e,))
        http_status(403)
