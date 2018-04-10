import pymongo, io, sys, os, json
import calendar

months = {}
for i ,v in enumerate(calendar.month_abbr):
	months[v] = i

from urllib.request import urlopen
import re
from crontab import CronTab
from datetime import datetime, timedelta
import logging
import math
from multiprocessing import Pool
import time

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate

import traceback

#time.sleep(60*60*11)

values = []
index = 0
flag = False

def eval_bandit():
	test_period = 'short'
	test_period = 'long'
	test_period = '100follow_short'
	test_period = '100follow_long'

	client = pymongo.MongoClient('localhost', 27017)

	# データベースを作成 (名前: my_database)
	db = client.Tweets

	# コレクションを作成 (名前: my_collection)

	#co = db.geo_tweet

	# なんか適当に保存
	#co.insert_one({"test": 3})
	#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

	#l_point = datetime.datetime(2017,5,26,20)-datetime.timedelta(hours=9) #終わる日時
	#t_point = datetime.datetime(2017,6,4,17)-datetime.timedelta(hours=9) #始める日時
	if test_period == 'short' or test_period == '100follow_short':
		start_point = datetime(2017,5,26,20)-timedelta(hours=9)
		end_point = datetime(2017,6,4,17)-timedelta(hours=9)
	elif test_period == 'long' or test_period == '100follow_long':
		start_point = datetime(2017,6,16,9)#-timedelta(hours=9) #始める日時
		end_point = datetime(2017,7,31,0)#-timedelta(hours=9) #終わる日時

	TimeWindow = 4
	total_W = math.ceil((end_point-start_point).total_seconds()/(60*60*TimeWindow)) - 1
	#total_W = 42
	if test_period == 'short' or test_period == '100follow_short':
		total_W = 52
	print(total_W)

	if test_period == 'short':
		path_follow_list_dir = 'follow_list_201712_short/'
		path_performance_result_list_dir = 'performance_result_list_201712_short/'
	elif test_period == 'long':
		path_follow_list_dir = 'follow_list_201712_long/'
		path_performance_result_list_dir = 'performance_result_list_201712_long/'
	elif test_period == '100follow_short':
		path_follow_list_dir = 'follow_list_201712_100follow_short/'
		path_performance_result_list_dir = 'performance_result_list_201712_100follow_short/'
	elif test_period == '100follow_long':
		path_follow_list_dir = 'follow_list_201712_100follow_long/'
		path_performance_result_list_dir = 'performance_result_list_201712_100follow_long/'

	experiment_ids = range(50)
	#region = 'tokyo'
	#regions = ['tsukuba']
	#regions = ['kyoto', 'tokyo', 'yokohama']
	#regions = ['kyoto_city', 'tokyo_23']
	#regions = ['kanagawa', 'ibaraki']
	#mode = ['epsilon-greedy', 'ucb', 'softmax', 'thompson sampling']
	#mode = ['d_ucb']
	#regions = ['kana']
	#regions = ['kana', 'kyoto', 'tokyo', 'ibaraki', 'kyoto_city', 'tokyo_23', 'yokohama', 'tsukuba']
	regions = ['tsukuba', 'tokyo_23', 'yokohama', 'kyoto_city']
	#regions = [regions[3]]
	#regions = ['yokohama', 'tsukuba']
	#i_region = int(sys.argv[1])
	#regions = regions[i_region:i_region+1]
	if test_period == 'short' or test_period == '100follow_short':
		f = open('user_id_to_data_for_eval_prepared_geo2_short.json', 'r')
	elif test_period == 'long' or test_period == '100follow_long':
		f = open('user_id_to_data_for_eval_prepared_geo2_long.json', 'r')
	user_id_to_data_for_eval = json.load(f)
	f.close()
	user_id_to_data_for_eval = user_id_to_data_for_eval.items()

	#mode = ['epsilon-greedy-follow-info', 'epsilon-greedy-new']
	#mode = ['epsilon-greedy-follow-info3-1','epsilon-greedy-follow-info4']
	#mode = ['epsilon-greedy-follow-info5', 'epsilon-greedy-follow-info3-quarter', 'epsilon-greedy-follow-info3-3quarter']
	#mode = ['epsilon-greedy-follow-info3-1','epsilon-greedy-new']

	#mode = ['epsilon-greedy-follow-info3-1', 'epsilon-greedy-new', 'random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics']
	#mode = ['epsilon-greedy-follow-info3-4quarter', 'epsilon-greedy-follow-info3-quarter', 'epsilon-greedy-follow-info3-3quarter', 'epsilon-greedy-follow-info3-1', 'epsilon-greedy-new']
	#mode = ['epsilon-greedy-follow-info6']
	#mode = ['epsilon-greedy-follow-info3-4quarter', 'epsilon-greedy-follow-info3-quarter', 'epsilon-greedy-follow-info3-3quarter']
	#mode = ['epsilon-greedy-follow-info3-1', 'epsilon-greedy-new', 'random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics']
	#mode = ['epsilon-greedy-follow-info3-1', 'epsilon-greedy-new', 'epsilon-greedy-retweet-info', 'epsilon-greedy-reply-info']#, 'epsilon-greedy-follow-info6']
	#mode = ['epsilon-greedy-with-follow-info-dynamic', 'epsilon-greedy-with-follow-info-4quarter', 'epsilon-greedy-with-follow-info-quarter', 'epsilon-greedy-with-follow-info-3quarter', 'epsilon-greedy-with-retweet-info', 'epsilon-greedy-with-reply-info']#, 'epsilon-greedy-with-follow-info', 'epsilon-greedy']
	mode = ['random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics', 'epsilon-greedy', 'epsilon-greedy-with-follow-info', 'epsilon-greedy-with-follow-info-4quarter', 'epsilon-greedy-with-follow-info-quarter', 'epsilon-greedy-with-follow-info-3quarter', 'epsilon-greedy-with-follow-info-dynamic', 'epsilon-greedy-with-follow-info-epsilon-decrease', 'epsilon-greedy-with-follow-info-epsilon-decrease-various-start']
	#mode = reversed(mode)
	#mode = ['epsilon-greedy-with-follow-info-epsilon-decrease2']
	#, 'epsilon-greedy-with-retweet-info', 'epsilon-greedy-with-reply-info', 'epsilon-greedy-with-retweet-info-quarter', 'epsilon-greedy-with-reply-info-quarter', 'epsilon-greedy-with-retweet-info-3quarter', 'epsilon-greedy-with-reply-info-3quarter', 'epsilon-greedy-with-retweet-info-4quarter', 'epsilon-greedy-with-reply-info-4quarter']#, 'epsilon-greedy-with-follow-info', 'epsilon-greedy']
	#mode = ['epsilon-greedy-with-follow-info-epsilon-decrease-various-start']
	#mode = ['epsilon-greedy-with-retweet-info-epsilon-decrease', 'epsilon-greedy-with-reply-info-epsilon-decrease']
	#mode = ['epsilon-greedy-with-retweet-info-epsilon-decrease-various-start', 'epsilon-greedy-with-reply-info-epsilon-decrease-various-start']
	#mode = ['random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics']
	modes_with_epsilon = ['epsilon-greedy', 'epsilon-greedy-with-follow-info', 'epsilon-greedy-with-follow-info-4quarter', 'epsilon-greedy-with-follow-info-quarter', 'epsilon-greedy-with-follow-info-3quarter', 'amount_of_tweets', 'epsilon-greedy-with-retweet-info', 'epsilon-greedy-with-reply-info', 'epsilon-greedy-with-retweet-info-quarter', 'epsilon-greedy-with-reply-info-quarter', 'epsilon-greedy-with-retweet-info-3quarter', 'epsilon-greedy-with-reply-info-3quarter', 'epsilon-greedy-with-retweet-info-4quarter', 'epsilon-greedy-with-reply-info-4quarter', 'epsilon-greedy-with-follow-info-epsilon-decrease2']
	for region in regions:
		if region == 'tsukuba':
			name_ja = u'つくば'
			name_en = u'Tsukuba'
			#co = db.tweets_per_user_long
		elif region == 'tokyo':
			name_ja = u'東京'
			name_en = u'Tokyo'
		elif region == 'kyoto':
			name_ja = u'京都'
			name_en = u'Kyoto'
		elif region == 'yokohama':
			name_ja = u'横浜'
			name_en = u'Yokohama'
			#co = db.tweets_per_user_long3

		elif region == 'tokyo_23':
			name_ja = u'東京'
			name_en = u'Tokyo'
			sub_ja = u'区'
			sub_en = u'-ku'
			#co = db.tweets_per_user_long2

		elif region == 'kyoto_city':
			name_ja = u'京都'
			name_en = u'Kyoto'
			sub_ja = u'区'
			sub_en = u'-ku'
			#co = db.tweets_per_user_long4

		elif region == 'kanagawa':
			name_ja = u'神奈川'
			name_en = u'Kanagawa'
		elif region == 'kana':
			name_ja = u'神奈'
			name_en = u'Kanagawa'
		elif region == 'ibaraki':
			name_ja = u'茨城'
			name_en = u'Ibaraki'

		if not os.path.isdir(path_performance_result_list_dir + region):
			os.makedirs(path_performance_result_list_dir + region)

		for m in mode:
			if m == 'epsilon-greedy-with-follow-info-dynamic' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease':
				params = [{'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.1}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.05}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.1}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.05}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.1}, {'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.05}, {'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.1}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.05}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.1}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.05}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.1}, {'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.05}, {'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.1}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.05}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.1}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.05}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.01},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.1}, {'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.05}, {'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.01}]

			elif m == 'epsilon-greedy-with-follow-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease-various-start':
				params = [{'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.1, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.5, 'threshold': 0.05, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.5, 'threshold': 0, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.1, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.7, 'threshold': 0.05, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.7, 'threshold': 0, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.1, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.05, 'start_alpha_rate': 0}, {'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.01, 'start_alpha_rate': 0},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.1, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.3, 'threshold': 0.05, 'delta': 0.01, 'start_alpha_rate': 0.25},
				{'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.1, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.05, 'start_alpha_rate': 0.25}, {'epsilon_plus_alpha': 0.3, 'threshold': 0, 'delta': 0.01, 'start_alpha_rate': 0.25}]
			elif m in modes_with_epsilon:
				params = [{'epsilon': 0.5}, {'epsilon': 0.7}, {'epsilon': 0.3}]
			else:
				params = [None]

			for p in params:
				#experiment_ids = reversed(list(range(10)))
				experiment_ids = range(50)
				for experiment_id in experiment_ids:
					if m == 'epsilon-greedy-with-follow-info-dynamic' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease-various-start' or m in modes_with_epsilon:
						input_path = path_follow_list_dir+region+'/follow_list_'+region+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun_long.csv'
						output_path = path_performance_result_list_dir+region+'/result_'+region+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun_long.csv'
					else:
						input_path = path_follow_list_dir+region+'/follow_list_'+region+'_'+m+'_'+str(experiment_id)+'_noun_long.csv'
						output_path = path_performance_result_list_dir+region+'/result_'+region+'_'+m+'_'+str(experiment_id)+'_noun_long.csv'

					if os.path.exists(input_path) and not os.path.exists(output_path):
						f = open(input_path, 'r')

						following_list = []
						for line in f:
							#print(line)
							tmp_following = line.strip('\n').split(',')
							if len(tmp_following) > 1:
								#tmp_following = list(map(float, tmp_following))
								for i,v in enumerate(tmp_following):
									if v.find('.')>-1:
										tmp_following[i] = v[:-2]
										#print(tmp_following[i])
								tmp_following = list(map(int, tmp_following))
								following_list.append(tmp_following)

						#following_list = following_list[100:200]
						#print(len(following_list[0]))
						results = []
						sum_result = 0
						previous_n_result = None
						previous_n_total = None
						for time_window_index, ids in enumerate(following_list):
							if time_window_index >= total_W:
								break
							print(time_window_index)
							n_result = 0
							n_total = 0
							n_none = 0
							sum_in_area = 0
							sum_out_area = 0
							start_point_tmp = start_point + timedelta(hours=4*time_window_index)
							end_point_tmp = start_point_tmp + timedelta(hours=4)
							flag_followed = {}
							for id in ids:
								flag_followed[id] = 1
							cnt_find = 0
							#for data in co.find(projection={'user_id': True, 'timestamp': True, 'geo': True}):
							cnt_followed = 0
							for user_id, data in user_id_to_data_for_eval:
								#cnt_find += 1
								#print(cnt_find)
								try:
									#flag_followed[data['user_id']]
									flag_followed[int(user_id)]
									#cnt_followed += 1
								except Exception:
									continue
								cnt_in_area = 0
								cnt_out_area = 0
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
								try:
									n_tweets = data['n_tweet_per_time_window'][str(time_window_index)]
								except Exception:
									n_tweets = data['n_tweet_per_time_window'][str(time_window_index) + '.0']

								sum_in_area += cnt_in_area
								sum_out_area += cnt_out_area
								"""
								if cnt_in_area > 0:
									n_true += cnt_in_area
								elif cnt_out_area == 0:
									if n_tweets > 0:
										n_none += n_tweets
								else:
									n_false += cnt_out_area
								"""
								if cnt_in_area > 0 or cnt_out_area > 0:
									n_result += n_tweets*cnt_in_area/(cnt_in_area + cnt_out_area)
									n_total += n_tweets
								else:
									n_none += n_tweets
							#print(cnt_followed)
							try:
								n_result += n_none * n_result / n_total
								previous_n_result = n_result
								previous_n_total = n_total
							except Exception:
								n_result += n_none * previous_n_result / previous_n_total
							sum_result += n_result
							print(sum_result)
							results.append(sum_result)
						#f = open('../result_tsukuba_softmax.csv', 'w')
						#f = open('../result_tsukuba_ts.csv', 'w')
						#f = open('../result_CMN_4NT150_follow_tsukuba.csv', 'w')
						#f = open('../result_tsukuba_ucb.csv', 'w')
						f = open(output_path, 'w')
						f.write(','.join(list(map(str, results))))
						f.close()
						print(results)
					else:
						if os.path.exists(input_path) and os.path.exists(output_path):
							f = open(output_path)
							for line in f:
								line = line.replace('\n', '').split(',')
								if len(line) != total_W:
									print(output_path)
									os.remove(output_path)
						#pass
						#print("There isn't new performance results")

class mem(object):
	def __init__(self, values, index, flag):
		self.values = values
		self.index = index
		self.flag = flag

	def get(self):
		return self.values, self.index, self.flag

	def set(self, values, index, flag):
		self.values = values
		self.index = index
		self.flag = flag

class JobConfig(object):
	"""
	処理設定
	"""

	def __init__(self, crontab, job):
		"""
		:type crontab: crontab.CronTab
		:param crontab: 実行時間設定
		:type job: function
		:param job: 実行する関数
		"""

		self._crontab = crontab
		self.job = job


	def schedule(self):
		crontab = self._crontab
		now_datetime = datetime.now()
		#return now_datetime + timedelta(seconds=10)
		return now_datetime + timedelta(minutes=1)

	def next(self):
		crontab = self._crontab
		now_datetime = datetime.now()
		return 6*1#-now_datetime.microsecond/1000000
		#return 10

def job_controller(jobConfig):
	#logging.info("->- 処理を開始しました。")

	while True:

		try:
			# 次実行日時を表示
			#logging.info("-?- 次回実行日時\tschedule:%s" % jobConfig.schedule().strftime("%Y-%m-%d %H:%M:%S"))

			# 次実行時刻まで待機
			time.sleep(jobConfig.next())

			#logging.info("-!> 処理を実行します。")

			# 処理を実行する。
			jobConfig.job()

			#logging.info("-!< 処理を実行しました。")

		except KeyboardInterrupt:
			break

	#logging.info("-<- 処理を終了終了しました。")


def job1():
	try:
		eval_bandit()
		print('cron:')
		print(str(datetime.now()))
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
		#print ('type:' + str(type(e)))
		#print ('args:' + str(e.args))
		#print ('message:' + e.message)
		print ('e自身:' + str(e))

def job2():
	logging.debug("処理2")


def main():
	# ログ設定
	#logging.basicConfig(level=logging.DEBUG,format="time:%(asctime)s.%(msecs)03d\tprocess:%(process)d" + "\tmessage:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

	# 毎分実行設定
	jobConfigs = [

	# 処理1を１分毎に実行する。
	JobConfig(CronTab("* * * * *"), job1),

	# 処理2を２分毎に実行する。
	#JobConfig(CronTab("*/2 * * * *"), job2)
	]

	# 処理を並列に実行
	p = Pool(len(jobConfigs))
	try:
		p.map(job_controller, jobConfigs)
	except KeyboardInterrupt:
		pass


if __name__ == "__main__":

	main()
