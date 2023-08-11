import json
import sys
import time
from base64 import b64decode, b64encode

import click
import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from opendatalab.__version__ import odl_clientId, uaa_url_prefix

api_login = "/api/v1/login/byClientSdk"
api_public_key = "/api/v1/cipher/getPubKey"
api_user_info = "/api/v1/login/getUserInfo"
api_auth = "/api/v1/internal/auth"


clientId = odl_clientId
public_key_url = uaa_url_prefix + api_public_key
login_url = uaa_url_prefix + api_login
user_info_url = uaa_url_prefix + api_user_info
auth_url = uaa_url_prefix + api_auth


def get_public_key():
    public_param = {"from": "browser", "type": "login", "clientId": clientId}  # "platform" "browser"
    data = json.dumps(public_param)
    resp = requests.post(url=public_key_url,
                         data=data,
                         headers={"Content-Type": "application/json"}
                         )

    result = ""
    if resp.status_code == 200:
        result = resp.json()['data']['pubKey']

    return result


def rsa_encrypt(content):
    public_key = get_public_key()
    key = b64decode(public_key)
    key = RSA.importKey(key)

    cipher = PKCS1_v1_5.new(key)
    cipher_text = b64encode(cipher.encrypt(bytes(content, 'utf-8')))

    return cipher_text


def get_account(account, password):
    timestamp_str = str(time.time()).split('.')[0]
    raw_text = f"{clientId}||{password}||{timestamp_str}"

    encrypt_key = rsa_encrypt(raw_text)
    key_str = encrypt_key.decode('utf-8')

    user_info = {'account': account, 'password': key_str, 'autoLogin': 'true'}
    data = json.dumps(user_info)

    resp = requests.post(url=login_url,
                         data=data,
                         headers={"Content-Type": "application/json"}
                         )

    result = None
    authorization = None
    sso_uid = None
    if resp.status_code == 200:
        result = resp.json()['data']

    if result:
        authorization = resp.headers['authorization']
        sso_uid = resp.json()['data']['ssoUid']
    else:
        click.secho(f"Error: Auth failure with account: {account}", err=True, fg="red")
        sys.exit(1)

    return authorization, sso_uid


def get_user_info(authorization):
    result = None
    if authorization:
        resp = requests.post(url=user_info_url,
                             headers={
                                 "Authorization": f"{authorization}",
                             }
                             )

        if resp.status_code == 200:
            result = resp.json()['data']['ssoUid']

    return result


def get_auth_code(sso_uid):
    result = None
    if sso_uid:
        client_id = {'clientId': clientId}
        data = json.dumps(client_id)

        resp = requests.post(url=auth_url,
                             data=data,
                             headers={
                                 "Content-Type": "application/json",
                                 "Cookie": f"ssouid={sso_uid}",
                             }
                             )
        if resp.status_code == 200:
            result = resp.json()['data']['code']

    return result


def get_odl_token(account, password):
    authorization, sso_uid = get_account(account=account, password=password)
    auth_code = None
    if sso_uid:
        auth_code = get_auth_code(sso_uid=sso_uid)

    if not auth_code:
        print(auth_code)
        click.secho(f"Error: Auth failure with account: {account}", err=True, fg="red")
        sys.exit(1)

    return auth_code
