import requests
from requests_oauthlib import OAuth1
import json, csv
from datetime import datetime, timedelta
import sys
import pymongo
import time


def lookup():
    client = pymongo.MongoClient('localhost', 27017)
    db = client.Tweets
    co = db.lookups

    f = open('setting.json', 'r')
    setting = json.load(f)
    f.close()

    f = open('data/top_geo_user_id_30000.json', 'r')
    user_list = json.load(f)
    f.close()

    auth = OAuth1(setting['api_key'], setting['api_secret'], setting['access_key'], setting['access_secret'])
    total_requests = len(user_list)//100
    if len(user_list) % 100 > 0:
        total_requests += 1
    for i in range(total_requests):
        try:
            ret = requests.get(setting['lookup_url'] + ','.join(user_list[100*i:100*(i+1)]), auth=auth)
        except Exception as e:
            print(e)
        for line in ret.iter_lines():
            lookups = json.loads(line)
            for l in lookups:
                co.save(l)
        if i % 300 == 299:
            time.sleep(60*15)
        else:
            time.sleep(1)

def make_existing_user_list():
    client = pymongo.MongoClient('localhost', 27017)
    db = client.Tweets
    co = db.lookups

    user_list_from_lookups = []
    for user in co.find(no_cursor_timeout=True):
        user_list_from_lookups.append(user['id_str'])

    f = open('data/top_geo_existing_user_id_30000.json', 'w')
    json.dump(user_list_from_lookups, f)
    f.close()

    print('%d existing users' % len(user_list_from_lookups))



if __name__ == '__main__':
    lookup()
    make_existing_user_list()
