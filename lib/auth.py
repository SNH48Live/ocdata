import argparse

import googleapiclient.discovery
import httplib2
import oauth2client.client
import oauth2client.file
import oauth2client.tools

from .config import CONFIGS_DIR


CLIENT_SECRETS_FILE = CONFIGS_DIR / 'client_secrets.json'
MISSING_CLIENT_SECRETS_MESSAGE = f'''
WARNING: Please configure OAuth 2.0 by downloading client_secrets.json from

  https://console.developers.google.com/apis/credentials?project=YOUR_PROJECT

and putting it at

  {CLIENT_SECRETS_FILE}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
'''


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        parents = list(kwargs.get('parents', []))
        parents.append(oauth2client.tools.argparser)
        kwargs['parents'] = parents
        super().__init__(**kwargs)


# oauth_scopes is a list of OAuth scopes with the
# https://www.googleapis.com/auth/ prefix stripped.
#
# In case only a single scope is needed, a single string is allowed in
# place of youtube_scopes, which is automatically understood as a
# singleton list.
def get_authenticated_http_client(oauth_scopes, args=None):
    if args is None:
        args = ArgumentParser().parse_args([])
    if isinstance(oauth_scopes, str):
        # Singleton
        oauth_scopes = [oauth_scopes]
    flow = oauth2client.client.flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=' '.join(f'https://www.googleapis.com/auth/{scope}' for scope in oauth_scopes),
        message=MISSING_CLIENT_SECRETS_MESSAGE,
    )
    oauth_credentials_file = CONFIGS_DIR / f'credentials-{",".join(oauth_scopes)}.json'
    storage = oauth2client.file.Storage(oauth_credentials_file)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = oauth2client.tools.run_flow(flow, storage, args)
    return credentials.authorize(httplib2.Http())


def get_google_api_client(service, version, scopes, args=None):
    http = get_authenticated_http_client(scopes, args=args)
    return googleapiclient.discovery.build(service, version, http=http)


# Typical scopes:
# - youtube
# - youtube.readonly
# - youtube.upload
def get_youtube_client(scopes, args=None):
    return get_google_api_client('youtube', 'v3', scopes, args=args)
