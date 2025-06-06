#!/usr/bin/python
'''
Author: Leo Lee (leejianzhao@gmail.com)
Date: 2021-07-18 16:34:45
LastEditTime: 2022-03-24 08:32:11
FilePath: \RSS\main.py
Description:
'''

import base64
import requests
import json
import time
import re
import base64
import os
import random
import datetime
import feedparser
import urllib
import yaml
import string

import urllib.parse
import urllib3
urllib3.disable_warnings()

dirs = './subscribe'

def log(msg):
    time = datetime.datetime.now()
    print('['+time.strftime('%Y.%m.%d-%H:%M:%S')+']:'+msg)

def IP2name(ip):
    return ip+''.join(random.sample(string.ascii_letters + string.digits, 8))

def protocol_decode(proxy_str):
    proxy={}
    proxy_str_split=proxy_str.split('://')
    if proxy_str_split[0] == 'trojan':
        pass
    elif proxy_str_split[0] == 'vmess':
        try:
            tmp=json.loads(base64.b64decode(proxy_str_split[1]+'=='))
            if tmp["add"]!='127.0.0.1':
                proxy={
                    "name"      :   IP2name(tmp.get("add")),
                    "type": "vmess",
                    "server": tmp.get("add"),
                    "port": tmp.get("port"),
                    "uuid": tmp.get("id"),
                    "alterId": tmp.get("aid"),
                    "cipher": "auto",
                    "network": tmp.get("net"),
                    'ucp':True,
                    'ws-path':tmp.get('path'),
                    'ws-headers':{'Host':tmp['host']} if tmp.__contains__('host') else None,
                    "tls": True if tmp.get("tls") == "tls" or tmp.get("net") == "h2" or tmp.get("net") == "grpc"else False,
                }
        except Exception as e:
            log('Invalid vmess URL:'+proxy_str)
            log(e.__str__())
    elif proxy_str_split[0] == 'ss':
        try:
            tmp=urllib.parse.urlparse(proxy_str)
            if tmp.username is not None:
                server=tmp.hostname
                port=tmp.port
                cipher,password=base64.b64decode(tmp.username+'==').decode().split(':')
            else:
                tmp=base64.b64decode(tmp.netloc+'==').decode()
                cipher,other,port=tmp.split(':')
                password,server=other.split('@')
            if cipher and ("chacha20-poly1305" not in cipher) and password and server and port:
                proxy={
                    "name"      :   IP2name(server),
                    "type": "ss",
                    "server": server,
                    "port": port,
                    "password": password,
                    "alterId": 2,
                    "cipher": cipher if cipher!="ss" else "aes-128-gcm",
                }
        except Exception as e:
            log('Invalid vmess URL:'+proxy_str)
            log(e.__str__())
    elif proxy_str_split[0] == 'ssr':
        proxy={}
    return proxy

def load_subscribe_url(url):
    if not url: return []
    log('begin load_subscribe_url: '+url)
    try:
        v2rayTxt = requests.request("GET", url, verify=False)
        sub=base64.b64decode(v2rayTxt.text+'==').decode('utf-8').splitlines()
        log(f'{url} import {len(sub)} servers')
        return sub
    except Exception as e:
        log('load_subscribe_url: '+url+': '+e.__str__())
        return []

def load_subscribe_url_txt(url):
    if not url: return []
    log('begin load_subscribe_url_txt: '+url)
    try:
        v2rayTxt = requests.request("GET", url, verify=False)
        sub=v2rayTxt.text.splitlines()
        log(f'{url} import {len(sub)} servers')
        return sub
    except Exception as e:
        log('load_subscribe_url: '+url+': '+e.__str__())
        return []

def load_subscribe(file):
    log('begin load local file: '+file)
    try:
        with open(file, 'rb') as f:
            raw=base64.b64decode(f.read()).decode('utf-8').splitlines()
            log(f'{file} import {len(raw)} servers')
            return raw
    except Exception as e:
        log('load_file: '+file+': '+e.__str__())
        return []

def gen_clash_subscribe(proxies):
    with open(r"./subscribe/config.yml", 'r', encoding='UTF-8') as f:
        config = yaml.safe_load(f)
    config['proxies']=proxies
    proxies_name=[proxies[i]['name'] for i in range(len(proxies))]
    config['proxy-groups'][0]['proxies'].extend(proxies_name)
    config['proxy-groups'][1]['proxies']=proxies_name
    with open(r"./subscribe/clash.yml",'w', encoding="utf-8") as f:
        yaml.dump(config,f, sort_keys=False,encoding="utf-8",allow_unicode=True)

def gen_v2ray_subscribe(proxies):
    with open(dirs + '/v2ray.txt','wb') as f:
        f.write(base64.b64encode('\n'.join(proxies).encode(encoding="ascii",errors="ignore")))

# 主函数入口
if __name__ == '__main__':
    log("RSS begin...")
    proxies=[]
    proxies.extend(load_subscribe(dirs + '/filtered.txt'))
    proxies.extend(load_subscribe_url_txt('https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt'))
    proxies.extend(load_subscribe_url('https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2'))
    proxies.extend(load_subscribe_url_txt('https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt'))
    proxies.extend(load_subscribe_url('https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub'))
    proxies.extend(load_subscribe_url('https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray'))
    proxies.extend(load_subscribe_url('https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub'))
    proxies.extend(load_subscribe_url('https://raw.githubusercontent.com/Pawdroid/Free-servers/refs/heads/main/sub'))
    now=datetime.date.today()
    proxies.extend(load_subscribe_url_txt(f"https://node.freeclashnode.com/uploads/{now.year:04}/{now.month:02}/0-{now.year:04}{now.month:02}{now.day:02}.txt"))
    proxies.extend(load_subscribe_url(f"https://node.freeclashnode.com/uploads/{now.year:04}/{now.month:02}/1-{now.year:04}{now.month:02}{now.day:02}.txt"))
    proxies.extend(load_subscribe_url_txt(f"https://node.freeclashnode.com/uploads/{now.year:04}/{now.month:02}/2-{now.year:04}{now.month:02}{now.day:02}.txt"))
    proxies.extend(load_subscribe_url(f"https://node.freeclashnode.com/uploads/{now.year:04}/{now.month:02}/3-{now.year:04}{now.month:02}{now.day:02}.txt"))
    proxies.extend(load_subscribe_url(f"https://node.freeclashnode.com/uploads/{now.year:04}/{now.month:02}/4-{now.year:04}{now.month:02}{now.day:02}.txt"))
    now+=datetime.timedelta(days=-1)
    proxies.extend(load_subscribe_url('https://flat-frost-62ae.leejianzhao.workers.dev/271828?b64'))
    proxies.extend(load_subscribe_url('https://flat-frost-62ae.leejianzhao.workers.dev/271828?sub=zrf.zrf.me'))
    proxies.extend(load_subscribe_url('https://flat-frost-62ae.leejianzhao.workers.dev/271828?sub=owo.o00o.ooo/ooo'))    
    proxies=list(set(proxies))
    gen_v2ray_subscribe(proxies)
    gen_clash_subscribe(list(filter(None,map(protocol_decode,proxies))))
