from asyncio import SubprocessTransport
import ssl
from typing import Any
from collections import OrderedDict
import requests
from requests.adapters import HTTPAdapter
import pandas
from threading import Thread
from re import compile


CIPHERS = [
	'ECDHE-ECDSA-AES128-GCM-SHA256',
	'ECDHE-ECDSA-CHACHA20-POLY1305',
	'ECDHE-RSA-AES128-GCM-SHA256',
	'ECDHE-RSA-CHACHA20-POLY1305',
	'ECDHE+AES128',
	'RSA+AES128',
	'ECDHE+AES256',
	'RSA+AES256',
	'ECDHE+3DES',
	'RSA+3DES'
]

class SSLAdapter(HTTPAdapter):
		def init_poolmanager(self, *a: Any, **k: Any) -> None:
			c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
			c.set_ciphers(':'.join(CIPHERS))
			k['ssl_context'] = c
			return super(SSLAdapter, self).init_poolmanager(*a, **k)

def auth():
    line = input("Account: ")
    username = line.split(":")[0].replace('\n', '')
    password = line.split(":")[1].replace('\n', '')
    session = requests.session()
    session.headers = OrderedDict({"User-Agent": "RiotClient/58.0.0.4640299.4552318 %s (Windows;10;;Professional, x64)","Accept-Language": "en-US,en;q=0.9","Accept": "application/json, text/plain, */*"})
    session.mount('https://', SSLAdapter()) 

    data = {"acr_values": "urn:riot:bronze","claims": "","client_id": "riot-client","nonce": "oYnVwCSrlS5IHKh7iI16oQ","redirect_uri": "http://localhost/redirect","response_type": "token id_token","scope": "openid link ban lol_region",}
    r = session.post(f'https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {'type': 'auth','username': username,'password': password}
    
    #Get token id and acces_token
    r = session.put(f'https://auth.riotgames.com/api/v1/authorization', json=data)
    data = r.json()

    if "access_token" in r.text:
        pattern = compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
        data = pattern.findall(data['response']['parameters']['uri'])[0]
        token = data[0]
        token_id = data[1]

    #Get Region
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    json = {"id_token": token_id}
    r = session.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=json)
    data = r.json()
    Region = data['affinities']['live']

    headers = {
            'User-Agent': "RiotClient/58.0.0.4640299.4552318 %s (Windows;10;;Professional, x64)",
            'Authorization': f'Bearer {token}',
        }
    #Get Emailverifed
    r3 = session.get("https://email-verification.riotgames.com/api/v1/account/status",headers=headers, json={})
    Emailverifed = r3.json()["emailVerified"]

    #Get Entitlements_token
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    entitlement = r.json()['entitlements_token']

    #Get Userinfo
    r = data = session.post("https://auth.riotgames.com/userinfo", headers=headers, json={})
    data = r.json()
    Sub = data['sub']
    data1 = data['acct']
    Name = data1['game_name']
    Tag = data1['tag_line']
    time4 = data1['created_at']
    time4 = int(time4)
    Createdat = pandas.to_datetime(time4,unit='ms')
    str(Createdat)
    print()
    print(f"Accestoken: {token}")
    print("-"*50)
    print(f"Entitlements: {entitlement}")
    print("-"*50)
    print(f"Userid: {Sub}")
    print("-"*50)
    print(f"Region: {Region}")
    print("-"*50)
    print(f"Emailverifed: {Emailverifed}")
    print("-"*50)
    print(f"Name: {Name}#{Tag}")
    print("-"*50)
    print(f"Createdat: {Createdat}")
    print("-"*50)

auth()
