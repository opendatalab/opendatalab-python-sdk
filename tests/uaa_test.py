import requests
import json
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode, b64decode

odl_dev_clientId = "qja9jy5wnjyqwvylmeqw"
odl_prd_clientId = "kmz3bkwzlaa3wrq8pvwa"

uaa_dev_url_prefix = "https://uaa-dev.openmmlab.com/gw/uaa-be"
uaa_prd_url_prefix = "https://sso.openxlab.org.cn/gw/uaa-be"

api_login = "/api/v1/login/byAccount"
api_public_key = "/api/v1/cipher/getPubKey"
api_user_info = "/api/v1/login/getUserInfo"
api_auth = "/api/v1/internal/auth"

is_prd_env = False

clientId = odl_prd_clientId if is_prd_env else odl_dev_clientId
uaa_url_prefix = uaa_prd_url_prefix if is_prd_env else uaa_dev_url_prefix

public_key_url = uaa_url_prefix + api_public_key
login_url = uaa_url_prefix + api_login
user_info_url = uaa_url_prefix + api_user_info
auth_url = uaa_url_prefix + api_auth
    


def get_public_key():
    public_param = {'from': "browser",'type': "login", "clientId": clientId} # "platform"
    data = json.dumps(public_param)
    resp = requests.post(url=public_key_url,
                         data = data,
                         headers={"Content-Type": "application/json"}
                         )
    
    result = ""
    if resp.status_code == 200:
        result  = resp.json()['data']['pubKey']
        # print(result)
    
    return result


def rsa_encrypt(content):
    public_key = get_public_key()
    key = b64decode(public_key)
    key = RSA.importKey(key)
    
    cipher = PKCS1_v1_5.new(key)
    cipher_text = b64encode(cipher.encrypt(bytes(content, 'utf-8')))
    
    return cipher_text


def get_account(account ,password):
    
    timestamp_str = str(time.time()).split('.')[0]    
    raw_text = f"{clientId}||{password}||{timestamp_str}"
    
    encrypt_key = rsa_encrypt(raw_text)
    key_str = encrypt_key.decode('utf-8')
    
    user_info = {'account' : account, 'password' : key_str, 'autoLogin': 'true'}
    data = json.dumps(user_info)

    resp = requests.post(url=login_url,
                         data = data,
                         headers={"Content-Type": "application/json"}
                         )
    
    result = None
    authorization = None
    if resp.status_code == 200:
        result  = resp.json()['data']
        # print(result)
    
    if result:
        authorization = resp.headers['authorization']
        
    
    return authorization


def get_user_info(authorization):
    result = None
    if authorization:
        resp = requests.post(url=user_info_url,
                             headers={
                                 "Authorization": f"{authorization}",
                                 }
                            )
    
        if resp.status_code == 200:
            result  = resp.json()['data']['ssoUid']
            # print(result)
        
    return result

def get_auth_code(ssouid):
    result = None
    if ssouid:
        client_id = {'clientId' : clientId}
        data = json.dumps(client_id)

        resp = requests.post(url=auth_url,
                             data = data,
                             headers={
                                 "Content-Type": "application/json",
                                 "Cookie": f"ssouid={ssouid}",
                                 }
                             )
        if resp.status_code == 200:
            result  = resp.json()['data']
            # print(result)
    
    return result    


def main():
    account = "someone@example.com" 
    pw = "password"
    
    authorization = get_account(account=account, password=pw)
    sso_uid = get_user_info(authorization=authorization) 
    auth_result = get_auth_code(ssouid=sso_uid)  


if __name__ == "__main__":
    main()    
    

