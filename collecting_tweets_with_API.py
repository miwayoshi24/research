import json
import sys
import time
import pymongo
import requests
import gzip
from collections import Counter
from requests_oauthlib import OAuth1
import math, calendar
from datetime import datetime, timedelta
import traceback

def is_japanese(text):
    def check_chr(x):
        return ((x >= 0x3040 and x <= 0x309f) or (x >= 0x30a0 and x <= 0x30ff))
    for ch in text:
        if check_chr(ord(ch)):
            return True
    return False

def collect_from_japan():
    client = pymongo.MongoClient('localhost', 27017)
    db = client.Tweets
    co = db.random_tweets

    f = open('setting.json', 'r')
    setting = json.load(f)
    f.close()

    auth = OAuth1(setting['api_key'], setting['api_secret'], setting['access_key'], setting['access_secret'])
    try:
        ret = requests.post(setting['filter_url'], auth=auth, stream=True, data={"locations":"122.87,24.84,153.01,46.80"})
    except Exception as e:
        print(e)


    for line in ret.iter_lines():
        try:
            tweet = json.loads(line)
            #if tweet['place'] is not None and tweet['place']['country'] == 'Japan':
            if tweet['place'] is not None and is_japanese(tweet['text']):
                co.save(tweet)
                # print(tweet)
        except Exception as e:
            print(e)

    print('interrupted')
    time.sleep(10)
    collect_from_japan()

def collect_from_follow_users():
    indexes = [0, 5000, 10000, 15000, 20000, 25000]
    client = pymongo.MongoClient('localhost', 27017)
    db = client.Tweets
    collections = [db.tweets_from_follow_users0, db.tweets_from_follow_users1, db.tweets_from_follow_users2 ,db.tweets_from_follow_users3, ]
    arg = int(sys.argv[1]) #コマンド例： python collecting_tweets_with_API.py 0

    co = collections[arg]
    index = indexes[arg]

    f = open('setting.json', 'r')
    setting = json.load(f)
    f.close()

    f = open('data/top_geo_existing_user_id_30000.json', 'r')
    user_list = json.load(f)
    f.close()
    if arg < 0:
        print('require arg >= 0')
        sys.exit()
    elif arg < 2:
        auth = OAuth1(setting['api_key'], setting['api_secret'], setting['access_key'], setting['access_secret'])
    elif arg < 4:
        auth = OAuth1(setting['api_key2'], setting['api_secret2'], setting['access_key2'], setting['access_secret2'])
    elif arg < 6:
        auth = OAuth1(setting['api_key3'], setting['api_secret3'], setting['access_key3'], setting['access_secret3'])
    else:
        print('require arg < 6')
        sys.exit()
    try:
        ret = requests.post(setting['filter_url'], auth=auth, stream=True, data={"follow":user_list[index:index+5000]})
    except Exception as e:
        print(e)


    for line in ret.iter_lines():
        try:
            tweet = json.loads(line)
            co.save(tweet)
        except Exception as e:
            print(e)

    print('interrupted')
    time.sleep(1)
    collect_from_follow_users()

def collect_follow_relationships():
    max_number_query_ids = 15
    client = pymongo.MongoClient('localhost', 27017)
    db = client.Tweets
    co = db.ids

    f = open('setting.json', 'r')
    setting = json.load(f)
    f.close()
    url_ids = setting['ids_url']

    f = open('data/top_geo_existing_user_id_30000.json', 'r')
    user_list = json.load(f)
    f.close()
    user_list = user_list[0:10000]
    # user_list = user_list[10000:20000]
    # user_list = user_list[20000:30000]
    auth = OAuth1(setting['api_key'], setting['api_secret'], setting['access_key'], setting['access_secret'])
    cnt_ids = 0
    for i, user_id in enumerate(user_list):
        print(i)
        if cnt_ids == max_query_ids:
            time.sleep(60 * 15 + 1)
            cnt_ids = 0
        obj = {'user_id':user_id, 'followings':[]}
        r = requests.get(url_ids+str(user_id), auth=auth)
        cnt_ids += 1
        for line in r.iter_lines():
            followings = json.loads(line)
            obj['followings'].append(followings)
            co.save(obj)

        while 'errors' not in followings and 'error' not in followings and followings['next_cursor'] > 0:
            if cnt_ids == max_query_ids:
                time.sleep(60 * 15 + 1)
                cnt_ids = 0
            url_ids_tmp = url_ids + str(user_id) + '&cursor=' + followings['next_cursor_str']
            r2 = requests.get(url_ids_tmp, auth=auth)
            cnt_ids += 1
            for line2 in r2.iter_lines():
                followings = json.loads(line2)
                obj['followings'].append(followings)
                co.save(obj)

def make_user_list_for_experiment():
    #start_point = datetime(2017,5,26,20)-timedelta(hours=9) #収集開始日時
    start_point = datetime(2017,6,16,9)#-timedelta(hours=9)
    #end_point = datetime(2017,6,4,17)-timedelta(hours=9) #終了日時
    end_point = datetime(2017,7,31,0)#-timedelta(hours=9)
    TimeWindow = 4
    total_W = math.ceil((end_point-start_point).total_seconds()/(60*60*TimeWindow))
    print(total_W)
    months = {}
    for i ,v in enumerate(calendar.month_abbr):
        months[v] = i

    client = pymongo.MongoClient('localhost', 27017)
    db = client.Tweets
    out = db.tweets_per_user4
    tweets_collections = [db.tweets_from_follow_users0, db.tweets_from_follow_users1, db.tweets_from_follow_users2 ,db.tweets_from_follow_users3]
    cnt = 0
    for col_tweets in tweets_collections:
        for tweet in col_tweets.find(no_cursor_timeout=True):
            try:
                datetime_parts = tweet['created_at'].split(" ")
                time_string = datetime_parts[5] + "-" + str(months[datetime_parts[1]]) + "-" + datetime_parts[2] + " " + datetime_parts[3]
                time_tmp = datetime.strptime(time_string,'%Y-%m-%d %H:%M:%S')
                if time_tmp > end_point:
                    break
                user_out = out.find_one({'user_id_str':tweet['user']['id_str']})
                if user_out == None:
                    if tweet['user']['id_str'] not in user_list:
                        continue
                    user_out = {'user_id':tweet['user']['id'], 'user_id_str':tweet['user']['id_str'], 'text':[], 'geo':[], 'tweet_id':[], 'timestamp':[]}
                if tweet['id'] in user_out['tweet_id']:
                    continue
                user_out['text'].append(tweet['text'])
                if tweet['place'] == None:
                    user_out['geo'].append(None)
                else:
                    user_out['geo'].append(tweet['place']['full_name'])
                #user_out['place'].append()
                user_out['tweet_id'].append(tweet['id'])
                user_out['timestamp'].append(tweet['created_at'])
                out.save(user_out)
                cnt += 1
                print(cnt)
            except Exception as e:
                ex, ms, tb = sys.exc_info()
                print("\nex -> \t",type(ex))
                print(ex)
                print("\nms -> \t",type(ms))
                print(ms)
                print("\ntb -> \t",type(tb))
                print(tb)

                print("\n=== and print_tb ===")
                traceback.print_tb(tb)
                print ('e自身:' + str(e))

    user_list = []
    for user in out.find(no_cursor_timeout=True):
        user_list.append(user['user_id'])
    f = open('data/user_list2.json')
    json.dump(user_list, f)
    f.close()

    cnt = 0
    link = 0
    link_dic = {}
    co_ids = db.ids
    for a_id in co_ids.find(no_cursor_timeout=True):
        try:
            if a_id['user_id'] in user_list:
                cnt += 1
                print(cnt)
                for followings in a_id['followings']:
                    if 'ids' in followings:
                        for id in followings['ids']:
                            id = int(id)
                            if id in user_list:
                                if a_id['user_id'] not in link_dic:
                                    link_dic[a_id['user_id']] = []
                                link_dic[a_id['user_id']].append(id)
                                #link += 1
        except Exception as e:
            print(e)

    f = open('data/link2.json', 'w')
    json.dump(link_dic, f)
    f.close()

if __name__ == '__main__':
    # collect_from_japan()
    collect_from_follow_users()
    collect_follow_relationships()
    make_user_list_for_experiment()
