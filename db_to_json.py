import pymongo, io, sys, os, json

client = pymongo.MongoClient('localhost', 27017)
db = client.Tweets
#co = db.tweets_per_user2#_long
co = db.tweets_per_user_long
"""
user_id_to_data_for_eval = {}
for data in co.find(projection={'user_id': True, 'timestamp': True, 'geo': True}):
    user_id_to_data_for_eval[data['user_id']] = {'timestamp': data['timestamp'], 'geo': data['geo']}

f = open('user_id_to_data_for_eval_long.json', 'w')
json.dump(user_id_to_data_for_eval, f)
f.close()

import calendar, math

months = {}
for i ,v in enumerate(calendar.month_abbr):
	months[v] = i

from datetime import datetime, timedelta

start_point = datetime(2017,6,16,9)#-timedelta(hours=9) #始める日時
end_point = datetime(2017,7,31,0)#-timedelta(hours=9) #終わる日時
#start_point = datetime(2017,5,26,20)-timedelta(hours=9)
#end_point = datetime(2017,6,4,17)-timedelta(hours=9)

TimeWindow = 4
total_W = math.ceil((end_point-start_point).total_seconds()/(60*60*TimeWindow))

f = open('user_id_to_data_for_eval_long.json', 'r')
user_id_to_data_for_eval = json.load(f)
f.close()
cnt = 0
for user_id, data in user_id_to_data_for_eval.items():
    cnt += 1
    print(cnt)
    user_id_to_data_for_eval[user_id]['flag_tweet_time_window'] = {}
    user_id_to_data_for_eval[user_id]['flag_geo'] = {}
    for i, timestamp_item in enumerate(data['timestamp']):
        datetime_parts = timestamp_item.split(" ")
        time_string = datetime_parts[5] + "-" + str(months[datetime_parts[1]]) + "-" + datetime_parts[2] + " " + datetime_parts[3]
        time_tmp = datetime.strptime(time_string,'%Y-%m-%d %H:%M:%S')
        time_window_index = (time_tmp - start_point).total_seconds()//14400
        user_id_to_data_for_eval[user_id]['flag_tweet_time_window'][time_window_index] = 1
        if user_id_to_data_for_eval[user_id]['geo'][i] is not None:
            try:
                user_id_to_data_for_eval[user_id]['flag_geo'][time_window_index][data['geo'][i]] = 1
            except Exception:
                user_id_to_data_for_eval[user_id]['flag_geo'][time_window_index] = {}
                user_id_to_data_for_eval[user_id]['flag_geo'][time_window_index][data['geo'][i]] = 1


f = open('user_id_to_data_for_eval_prepared_geo_long.json', 'w')
json.dump(user_id_to_data_for_eval, f)
f.close()
#

f = open('user_id_to_data_for_eval_prepared_geo_long.json', 'r')
user_id_to_data_for_eval = json.load(f)
f.close()
cnt = 0
for user_id, data in user_id_to_data_for_eval.items():
    cnt += 1
    print(cnt)
    #user_id_to_data_for_eval[user_id]['flag_tweet_time_window'] = {}
    #user_id_to_data_for_eval[user_id]['flag_geo'] = {}
    user_id_to_data_for_eval[user_id]['n_tweet_per_time_window'] = {}
    for i, timestamp_item in enumerate(data['timestamp']):
        datetime_parts = timestamp_item.split(" ")
        time_string = datetime_parts[5] + "-" + str(months[datetime_parts[1]]) + "-" + datetime_parts[2] + " " + datetime_parts[3]
        time_tmp = datetime.strptime(time_string,'%Y-%m-%d %H:%M:%S')
        time_window_index = (time_tmp - start_point).total_seconds()//14400
        try:
            user_id_to_data_for_eval[user_id]['n_tweet_per_time_window'][time_window_index] += 1
        except Exception:
            user_id_to_data_for_eval[user_id]['n_tweet_per_time_window'][time_window_index] = 1


f = open('user_id_to_data_for_eval_prepared_geo2_long.json', 'w')
json.dump(user_id_to_data_for_eval, f)
f.close()

#

regions = ['tsukuba', 'tokyo_23', 'yokohama', 'kyoto_city']
for region in regions:
    if region == 'tsukuba':
        col_user = db.tweets_per_user_long
    elif region == 'tokyo_23':
        col_user = db.tweets_per_user_long2
    elif region == 'kyoto_city':
        col_user = db.tweets_per_user_long4
    elif region == 'yokohama':
        col_user = db.tweets_per_user_long3
    user_id_to_data_for_prob = {}
    cnt = 0
    for data in col_user.find(projection={'prob_list_' + region + '_noun': True, 'user_id': True }):
        cnt += 1
        print(region + ': %d' % cnt)
        user_id_to_data_for_prob[data['user_id']] = data['prob_list_' + region + '_noun']

    f = open('user_id_to_data_for_prob_' + region + '_long.json', 'w')
    json.dump(user_id_to_data_for_prob, f)
    f.close()
"""
#
"""
tweets_collections = [db.tweets_20170616_0, db.tweets_20170616_1, db.tweets_20170616_2, db.tweets_20170616_3]
col_user = db.tweets_per_user_long
flag_user_id = {}
for data in col_user.find(projection={'user_id': True }):
    flag_user_id[data['user_id']] = 1
n_candidate = len(flag_user_id)
screen_name_to_user_id = {}
cnt = 0
for col_tweets in tweets_collections:
    for tweet in col_tweets.find(no_cursor_timeout=True):
        try:
            flag_user_id[tweet['user']['id']]
            try:
                screen_name_to_user_id[tweet['user']['screen_name']]
            except Exception:
                screen_name_to_user_id[tweet['user']['screen_name']] = tweet['user']['id']
                cnt += 1
                print(cnt)
                if cnt == n_candidate:
                    f = open('screen_name_to_user_id_long', 'w')
                    json.dump(screen_name_to_user_id, f)
                    f.close()
                    sys.exit()
        except Exception:
            pass
"""
#
total_W = 52
f = open('user_id_to_data_for_eval_prepared_geo2_short.json', 'r')
#f = open('user_id_to_data_for_eval_prepared_geo2_long.json', 'r')
user_id_to_data_for_eval = json.load(f)
f.close()
user_id_to_data_for_eval = user_id_to_data_for_eval.items()
cnt_geotag = {}
regions = ['tsukuba', 'tokyo_23', 'yokohama', 'kyoto_city']

for region in regions:
    cnt_geotag[region] = []
    if region == 'tsukuba':
        name_ja = u'つくば'
        name_en = u'Tsukuba'
    elif region == 'tokyo':
        name_ja = u'東京'
        name_en = u'Tokyo'
    elif region == 'kyoto':
        name_ja = u'京都'
        name_en = u'Kyoto'
    elif region == 'yokohama':
        name_ja = u'横浜'
        name_en = u'Yokohama'
    elif region == 'tokyo_23':
        name_ja = u'東京'
        name_en = u'Tokyo'
        sub_ja = u'区'
        sub_en = u'-ku'
    elif region == 'kyoto_city':
        name_ja = u'京都'
        name_en = u'Kyoto'
        sub_ja = u'区'
        sub_en = u'-ku'
    elif region == 'kanagawa':
        name_ja = u'神奈川'
        name_en = u'Kanagawa'
    elif region == 'kana':
        name_ja = u'神奈'
        name_en = u'Kanagawa'
    elif region == 'ibaraki':
        name_ja = u'茨城'
        name_en = u'Ibaraki'
    for time_window_index in range(total_W):
        cnt_in_area = 0
        cnt_out_area = 0
        print(region)
        print(time_window_index)
        for user_id, data in user_id_to_data_for_eval:
            #data = co.find_one({'user_id':id}, projection={'timestamp': True, 'geo': True})
            try:
                #print(data['flag_geo'])
                geoes = data['flag_geo'][str(time_window_index)].keys()
                #print('geoes')
            except Exception:
                try:
                    geoes = data['flag_geo'][str(time_window_index) + '.0'].keys()
                except Exception:
                    continue
            for geo in geoes:
                if name_ja == u'茨城':
                    if name_ja in geo or (name_en in geo and 'Osaka' not in geo):
                        #if (name_ja in data['geo'][i] and sub_ja in data['geo'][i]) or (name_en in data['geo'][i] and sub_en in data['geo'][i]):
                        cnt_in_area += 1
                    else:
                        cnt_out_area += 1
                elif region == 'tokyo_23' or region == 'kyoto_city':
                    if (name_ja in geo and sub_ja in geo) or (name_en in geo and sub_en in geo):
                        cnt_in_area += 1
                    else:
                        cnt_out_area += 1
                else:
                    if name_ja in geo or name_en in geo:
                        #if (name_ja in data['geo'][i] and sub_ja in data['geo'][i]) or (name_en in data['geo'][i] and sub_en in data['geo'][i]):
                        cnt_in_area += 1
                    else:
                        cnt_out_area += 1
        cnt_geotag[region].append(cnt_in_area)
f = open('cnt_geotag_short.json', 'w')
#f = open('cnt_geotag_long.json', 'w')
json.dump(cnt_geotag, f)
f.close()
