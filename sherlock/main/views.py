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



APP_KEY = 'nice try'
APP_SECRET = 'not happening'

conn = DBConnector()

def get_dropbox_auth_flow(web_app_session):
    redirect_uri = "https://watson.local.codef.in/auth_finish"
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
    print info
    return render_to_response('index.html', {"user": info})

def search(request):
    time.sleep(1);
    response_data = [{
        "name": "owl",
        "image": get_image('http://i.imgur.com/HTYTD3Y.jpg')
    }, {
        "name": "trees",
        "image": get_image('http://i.imgur.com/RLJbxDS.jpg')
    }, {
        "name": "dog",
        "image": get_image('http://i.imgur.com/r0YeLYV.jpg')
    }, {
        "name": "grand central",
        "image": get_image('http://i.imgur.com/ao7XZj4.jpg')
    }, {
        "name": "dragon",
        "image": get_image('http://i.imgur.com/SEs8Xky.jpg')
    }, {
        "name": "frozen truck",
        "image": get_image('http://i.imgur.com/OYsHKlH.jpg')
    }];
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_image(url):
    return base64.b64encode(urllib2.urlopen(url).read())

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
