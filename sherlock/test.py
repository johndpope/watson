import dropbox

# Get your app key and secret from the Dropbox developer website
app_key = 'nice try'
app_secret = 'not happening'

access_token = 'safety first'
client = dropbox.client.DropboxClient(access_token)
print 'linked account: ', client.account_info()
print access_token
