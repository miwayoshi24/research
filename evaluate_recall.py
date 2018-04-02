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

def eval_bandit():
	f = open('exp_setting.json', 'r')
	setting = json.load(f)
	f.close()
	areas = setting['areas']
	TimeWindow = setting['TimeWindow'] #タイムウィンドウ幅（hour）
	K = setting['K'] #タイムウィンドウ幅（hour）
	test_period = setting['test_period']

	if test_period == 'short':
		start_point = datetime(2017,5,26,20)-timedelta(hours=9)
		end_point = datetime(2017,6,4,17)-timedelta(hours=9)
	elif test_period == 'long':
		start_point = datetime(2017,6,16,9)#-timedelta(hours=9) #始める日時
		end_point = datetime(2017,7,31,0)#-timedelta(hours=9) #終わる日時

	total_W = math.ceil((end_point-start_point).total_seconds()/(60*60*TimeWindow)) - 1
	if test_period == 'short':
		total_W = 52
	print(total_W)

	if test_period == 'short':
		f = open('data/user_id_to_data_for_eval_prepared_geo2_short.json', 'r')
	elif test_period == 'long':
		f = open('data/user_id_to_data_for_eval_prepared_geo2_long.json', 'r')
	user_id_to_data_for_eval = json.load(f)
	f.close()
	user_id_to_data_for_eval = user_id_to_data_for_eval.items()

	path_follow_list_dir = setting['directory_for_follow_list']
	path_result_recall_dir = setting['directory_for_result_recall']

	start_exp_id = int(sys.argv[1])
	n_exp = int(sys.argv[2])
	experiment_ids = range(start_exp_id, start_exp_id + n_exp)

	if test_period == 'short':
		f = open('data/cnt_geotag_short.json', 'r')
	elif test_period == 'long':
		f = open('data/cnt_geotag_long.json', 'r')
	cnt_geotag = json.load(f)
	f.close()

	mode = setting['mode']
	for area in areas:
		if area == 'tsukuba':
			name_ja = u'つくば'
			name_en = u'Tsukuba'
		elif area == 'tokyo':
			name_ja = u'東京'
			name_en = u'Tokyo'
		elif area == 'kyoto':
			name_ja = u'京都'
			name_en = u'Kyoto'
		elif area == 'yokohama':
			name_ja = u'横浜'
			name_en = u'Yokohama'
		elif area == 'tokyo_23':
			name_ja = u'東京'
			name_en = u'Tokyo'
			sub_ja = u'区'
			sub_en = u'-ku'
		elif area == 'kyoto_city':
			name_ja = u'京都'
			name_en = u'Kyoto'
			sub_ja = u'区'
			sub_en = u'-ku'
		elif area == 'kanagawa':
			name_ja = u'神奈川'
			name_en = u'Kanagawa'
		elif area == 'kana':
			name_ja = u'神奈'
			name_en = u'Kanagawa'
		elif area == 'ibaraki':
			name_ja = u'茨城'
			name_en = u'Ibaraki'

		if not os.path.isdir(path_result_recall_dir + area):
			os.makedirs(path_result_recall_dir + area)

		for m in mode:
			params = []
			if m in ['epsilon_greedy', 'amount_of_tweets']:
				epsilon_list = setting['param']['epsilon']
				for epsilon in epsilon_list:
					params.append({'epsilon' : epsilon})
			elif m == 'epsilon_alpha_greedy_static':
				epsilon_plus_alpha_list = setting['param']['epsilon_plus_alpha']
				alpha_rate_list = setting['param']['alpha_rate']
				for epsilon_plus_alpha in epsilon_plus_alpha_list:
					for alpha_rate in alpha_rate_list:
						params.append({'epsilon_plus_alpha' : epsilon_plus_alpha, 'alpha_rate' : alpha_rate})
			elif m == 'epsilon_alpha_greedy_dynamic':
				epsilon_plus_alpha_list = setting['param']['epsilon_plus_alpha']
				start_alpha_rate_list = setting['param']['start_alpha_rate']
				threshold_list = setting['param']['threshold']
				delta_list = setting['param']['delta']
				for epsilon_plus_alpha in epsilon_plus_alpha_list:
					for start_alpha_rate in start_alpha_rate_list:
						for threshold in threshold_list:
							for delta in delta_list:
								params.append({'epsilon_plus_alpha' : epsilon_plus_alpha, 'start_alpha_rate' : start_alpha_rate, 'threshold' : threshold, 'delta' : delta})
			else:
				params.append(None)

			for p in params:
				for experiment_id in experiment_ids:
					if p is None:
						input_path = path_follow_list_dir+area+'/follow_list_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
						output_path = path_result_recall_dir+area+'/n_geotags_in_area_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
						recall_output_path = path_result_recall_dir+area+'/recall_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
						output_path_acc = path_result_recall_dir+area+'/n_geotags_in_area_accumulated_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
						recall_output_path_acc = path_result_recall_dir+area+'/recall_accumulated_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
					else:
						input_path = path_follow_list_dir+area+'/follow_list_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'
						output_path = path_result_recall_dir+area+'/n_geotags_in_area_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'
						recall_output_path = path_result_recall_dir+area+'/recall_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'
						output_path_acc = path_result_recall_dir+area+'/n_geotags_in_area_accumulated_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'
						recall_output_path_acc = path_result_recall_dir+area+'/recall_accumulated_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'

					if os.path.exists(input_path) and not os.path.exists(output_path):
						f = open(input_path, 'r')

						following_list = []
						for line in f:
							tmp_following = line.strip('\n').split(',')
							if len(tmp_following) > 1:
								for i,v in enumerate(tmp_following):
									if v.find('.')>-1:
										tmp_following[i] = v[:-2]
								tmp_following = list(map(int, tmp_following))
								following_list.append(tmp_following)

						n_geotags = []
						recalls = []
						accumulated_n_geotags = []
						accumulated_recalls = []
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
							cnt_followed = 0
							for user_id, data in user_id_to_data_for_eval:
								try:
									flag_followed[int(user_id)]
								except Exception:
									continue
								cnt_in_area = 0
								cnt_out_area = 0
								try:
									geoes = data['flag_geo'][str(time_window_index)].keys()
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
									elif area == 'tokyo_23' or area == 'kyoto_city':
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
								if cnt_in_area > 0 or cnt_out_area > 0:
									n_result += n_tweets*cnt_in_area/(cnt_in_area + cnt_out_area)
									n_total += n_tweets
								else:
									n_none += n_tweets
							recalls.append(sum_in_area/cnt_geotag[area][time_window_index])
							try:
								accumulated_n_geotags.append(accumulated_n_geotags[-1] + sum_in_area)
								accumulated_recalls.append(accumulated_n_geotags[-1]/sum(cnt_geotag[area][:time_window_index+1]))
							except Exception:
								print('time window: ' + str(time_window_index))
								if time_window_index != 0:
									sys.exit()
								accumulated_n_geotags.append(sum_in_area)
								accumulated_recalls.append(recalls[0])
							n_geotags.append(sum_in_area)


							try:
								n_result += n_none * n_result / n_total
								previous_n_result = n_result
								previous_n_total = n_total
							except Exception:
								n_result += n_none * previous_n_result / previous_n_total
							sum_result += n_result
							print(sum_in_area)

						f = open(output_path, 'w')
						f.write(','.join(list(map(str, n_geotags))))
						f.close()
						f = open(recall_output_path, 'w')
						f.write(','.join(list(map(str, recalls))))
						f.close()
						f = open(output_path_acc, 'w')
						f.write(','.join(list(map(str, accumulated_n_geotags))))
						f.close()
						f = open(recall_output_path_acc, 'w')
						f.write(','.join(list(map(str, accumulated_recalls))))
						f.close()

					else:
						if os.path.exists(input_path) and os.path.exists(output_path):
							f = open(output_path)
							for line in f:
								line = line.replace('\n', '').split(',')
								if len(line) != total_W:
									print(output_path)
									os.remove(output_path)


if __name__ == "__main__":
	while True:
		eval_bandit()
		time.sleep(60*10)
