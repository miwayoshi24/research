import gzip
import json
import time
import os
import sys
from collections import Counter

def count_geo_per_file():
    f = open('setting.json', 'r')
    setting = json.load(f)
    f.close()

    if not os.path.isdir('data/geo_user_count'):
        os.makedirs('data/geo_user_count')

    for i in range(0,16285):
        try:
            geo_cnt = 0
            id_count = {}
            start = time.time()
            path = setting['path_tweets_HDD'] + str(i) + setting['extention_tweets_HDD']
            with gzip.open(path, 'r') as f:
                for line in f:
                    obj = json.loads(line)
                    try:
                        obj['place']['full_name']
                        geo_cnt += 1
                        user_id_str = obj['user']['id_str']
                        try:
                            id_count[user_id_str] += 1
                        except Exception:
                            id_count[user_id_str] = 1
                    except Exception:
                        pass
            print('file No.%d : %d geo tagged tweets' % (i, geo_cnt))


            f = open('data/geo_user_count/'+str(i)+'.json', 'w')
            json.dump(id_count, f)
            f.close()
            elapsed_time = time.time() - start
            print (('elapsed_time: {0} [sec]'.format(elapsed_time)))
        except Exception as e:
            print(e)

def sum_count_geo():
    id_count = {}
    for i in range(16285):
        print(i)
        try:
            start = time.time()
            f = open('data/geo_user_count/'+str(i)+'.json', 'r')
            for line in f:
                obj = json.loads(line)
                id_count = dict(Counter(id_count) + Counter(obj))

            elapsed_time = time.time() - start
            print(("elapsed_time: {0} [sec]".format(elapsed_time)))
        except Exception as e:
            print(e)

    f = open('data/geo_user_count/sum.json', 'w')
    json.dump(id_count, f)
    f.close()

def sellect_top_geo_users():
    n_top_users = 30000
    limmit_n_geo_tweets = 2000
    f = open('data/geo_user_count/sum.json', 'r')
    for line in f:
        id_count = json.loads(line)
    f.close()
    print('loaded')

    start = time.time()
    users = sorted(id_count.items(), key=lambda x: x[1], reverse=True)
    elapsed_time = time.time() - start
    print('sorted')
    print (("elapsed_time: {0} [sec]".format(elapsed_time)))

    blacklist = []
    for item in users:
        if item[1] >= limmit_n_geo_tweets:
            blacklist.append(item[0])
        else:
            break
    print(blacklist)

    f = open('data/blacklist.json', 'w')
    json.dump(blacklist, f)
    f.close()

    top_geo_user = users[:n_top_users+len(blacklist)]
    top_geo_user_id = []
    for v in top_geo_user:
        top_geo_user_id.append(v[0])
    f = open('data/top_geo_user_id_%d.json' % n_top_users, 'w')
    json.dump(top_geo_user_id, f)
    f.close()

if __name__ == '__main__':
    # count_geo_per_file()
    # sum_count_geo()
    sellect_top_geo_users()
