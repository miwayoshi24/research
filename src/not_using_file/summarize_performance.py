import pymongo, io, sys, os
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

import numpy as np
import json

values = []
index = 0
flag = False

def sum_perfo():
	n_exp = 50
	offset = 0
	experiment_ids = range(offset, n_exp+offset)
	N_TW = 267
	#N_TW = 52
	#region = 'tokyo'
	regions = ['tsukuba']
	regions = ['kyoto_city', 'tokyo_23']
	regions = ['ibaraki', 'kanagawa']
	regions = ['kana']
	regions = ['tokyo_23', 'tsukuba', 'yokohama', 'kyoto_city']
	#dir_name = 'performance_result_list_201712_short/'
	dir_name = 'performance_result_list_201712_long/'
	#dir_name = 'performance_result_list_201712_100follow_short/'
	#dir_name = 'performance_result_list_201712_100follow_long/'

	#dir_name = 'performance_result_201711/'
	#regions = ['tokyo_23']
	#regions = ['tsukuba']
	#regions = ['kyoto', 'tokyo', 'yokohama']
	#mode = ['epsilon-greedy', 'ucb', 'softmax', 'thompson sampling']
	#mode = ['d_ucb']
	mode = ['epsilon-greedy-follow-info', 'epsilon-greedy-new']
	mode = ['epsilon-greedy-follow-info3-1','epsilon-greedy-follow-info4']
	mode = ['epsilon-greedy-new', 'epsilon-greedy-follow-info3-1', 'epsilon-greedy-follow-info4', 'epsilon-greedy-follow-info5', 'epsilon-greedy-follow-info3-quarter', 'epsilon-greedy-follow-info3-3quarter']
	mode = ['epsilon-greedy-follow-info3-1','epsilon-greedy-new']

	mode = ['random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics']
	mode = ['epsilon-greedy-follow-info3-1', 'epsilon-greedy-new', 'random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics']
	mode = ['epsilon-greedy-follow-info6']
	mode = ['epsilon-greedy-new']
	mode = ['random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics', 'epsilon-greedy-new', 'epsilon-greedy-follow-info3-1', 'epsilon-greedy', 'epsilon-greedy-with-follow-info', 'epsilon-greedy-with-follow-info-dynamic', 'epsilon-greedy-with-follow-info-4quarter', 'epsilon-greedy-with-follow-info-quarter', 'epsilon-greedy-with-follow-info-3quarter', 'epsilon-greedy-with-follow-info-epsilon-decrease', 'epsilon-greedy-with-follow-info-epsilon-decrease-various-start']#, 'epsilon-greedy-with-follow-info-epsilon-decrease2']
	#, 'epsilon-greedy-with-retweet-info', 'epsilon-greedy-with-retweet-info-quarter', 'epsilon-greedy-with-retweet-info-3quarter', 'epsilon-greedy-with-retweet-info-4quarter', 'epsilon-greedy-with-retweet-info-epsilon-decrease', 'epsilon-greedy-with-retweet-info-epsilon-decrease-various-start', 'epsilon-greedy-with-reply-info', 'epsilon-greedy-with-reply-info-quarter', 'epsilon-greedy-with-reply-info-3quarter', 'epsilon-greedy-with-reply-info-4quarter', 'epsilon-greedy-with-reply-info-epsilon-decrease', 'epsilon-greedy-with-reply-info-epsilon-decrease-various-start']
	#, 'epsilon-greedy-with-retweet-info', 'epsilon-greedy-with-reply-info']#, 'epsilon-greedy-with-follow-info', 'epsilon-greedy']
	#mode = ['random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics', 'epsilon-greedy-with-follow-info-epsilon-decrease']
	modes_with_epsilon = ['epsilon-greedy', 'epsilon-greedy-with-follow-info', 'epsilon-greedy-with-follow-info-4quarter', 'epsilon-greedy-with-follow-info-quarter', 'epsilon-greedy-with-follow-info-3quarter', 'amount_of_tweets', 'epsilon-greedy-with-retweet-info', 'epsilon-greedy-with-reply-info', 'epsilon-greedy-with-retweet-info-quarter', 'epsilon-greedy-with-reply-info-quarter', 'epsilon-greedy-with-retweet-info-3quarter', 'epsilon-greedy-with-reply-info-3quarter', 'epsilon-greedy-with-retweet-info-4quarter', 'epsilon-greedy-with-reply-info-4quarter', 'epsilon-greedy-with-follow-info-epsilon-decrease2']
	#mode = ['epsilon-greedy-follow-info3-1', 'epsilon-greedy-new', 'random', 'amount_of_tweets', '6TWStatistics', '18TWStatistics']
	"""param = [{'threshold':0.1, 'delta':0.05}, {'threshold':0.1, 'delta':0.01}, {'threshold':0.1, 'delta':0.1},
	{'threshold':0.2, 'delta':0.05}, {'threshold':0.2, 'delta':0.01}, {'threshold':0.2, 'delta':0.1},
	{'threshold':0.05, 'delta':0.05}, {'threshold':0.05, 'delta':0.01}, {'threshold':0.05, 'delta':0.1}]
	param = [{'threshold':0.05, 'delta':0.05}, {'threshold':0.1, 'delta':0.05}, {'threshold':0.2, 'delta':0.01}]"""


	for region in regions:
		result = {}
		n_tweets_and_std = {}
		best = {}
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
				reward_list = []

				if m == 'epsilon-greedy-with-follow-info-dynamic' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease-various-start' or m in modes_with_epsilon:
					input_mode = m+'_'+str(p)
				else:
					input_mode = m
				for experiment_id in experiment_ids:
					#input_path = 'performance_result/'+region+'/result_'+region+'_'+m+'_'+str(experiment_id)+'_new_'+data_kind+'.csv'
					if m == 'epsilon-greedy-with-follow-info-dynamic' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease' or m == 'epsilon-greedy-with-follow-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-retweet-info-epsilon-decrease-various-start' or m == 'epsilon-greedy-with-reply-info-epsilon-decrease-various-start' or m in modes_with_epsilon:
						input_path = dir_name+region+'/result_'+region+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun_long.csv'
					else:
						input_path = dir_name+region+'/result_'+region+'_'+m+'_'+str(experiment_id)+'_noun_long.csv'

					if os.path.exists(input_path):
						f = open(input_path, 'r')
						for line in f:
							#print(line)
							tmp_reward = line.strip('\n').split(',')
							if len(tmp_reward) > 1:
								#tmp_following = list(map(float, tmp_following))
								tmp_reward = list(map(float, tmp_reward))
								if len(tmp_reward) < N_TW:
									print(input_path)
									print(len(tmp_reward))
									print(tmp_reward)
								reward_list.append(tmp_reward)

					else:
						print('no')
				if len(reward_list)==n_exp:
					reward_mean = []
					n_tweets_and_std[input_mode] = {'n_tweets':[], 'std':0}
					for r in reward_list:
						#n_tweets_and_std[input_mode]['n_tweets'].append(r[-1])
						#print(len(r))
						#print(input_path)
						n_tweets_and_std[input_mode]['n_tweets'].append(r[N_TW-1])
					n_tweets_and_std[input_mode]['std'] = np.std(np.array(n_tweets_and_std[input_mode]['n_tweets']))

					#for t in range(len(reward_list[0])):
					for t in range(N_TW):
						tmp_reward_mean = 0
						for i in experiment_ids:
							tmp_reward_mean += reward_list[i-offset][t]
						tmp_reward_mean /= n_exp
						reward_mean.append(tmp_reward_mean)
					result[input_mode] = reward_mean
					if m not in best:
						best[m] = {}
						best[m]['param'] = p
						best[m]['mean'] = result[input_mode][N_TW-1]
						best[m]['input_mode'] = input_mode
					elif result[input_mode][N_TW-1] > best[m]['mean']:
						best[m]['param'] = p
						best[m]['mean'] = result[input_mode][N_TW-1]
						best[m]['input_mode'] = input_mode

					"""print(m)
					print(region)
					print(reward_mean)"""

		#output_path = dir_name+region+'/result_'+region+'_sum_noun_compare_20171228_short.csv'
		#output_path_std = dir_name+region+'/result_'+region+'_n_tweets_and_std_noun_compare_20171228_short.csv'
		#output_path_best = dir_name+region+'/result_'+region+'_best_param_noun_compare_20171228_short.csv'

		output_path = dir_name+region+'/result_'+region+'_sum_noun_compare_20171228_long.csv'
		output_path_std = dir_name+region+'/result_'+region+'_n_tweets_and_std_noun_compare_20171228_long.csv'
		output_path_best = dir_name+region+'/result_'+region+'_best_param_noun_compare_20171228_long.csv'

		"""output_path = dir_name+region+'/result_'+region+'_sum_noun_compare_20171228_100follow_short.csv'
		output_path_std = dir_name+region+'/result_'+region+'_n_tweets_and_std_noun_compare_20171228_100follow_short.csv'
		output_path_best = dir_name+region+'/result_'+region+'_best_param_noun_compare_20171228_100follow_short.csv'"""

		"""output_path = dir_name+region+'/result_'+region+'_sum_noun_compare_20171228_100follow_long.csv'
		output_path_std = dir_name+region+'/result_'+region+'_n_tweets_and_std_noun_compare_20171228_100follow_long.csv'
		output_path_best = dir_name+region+'/result_'+region+'_best_param_noun_compare_20171228_100follow_long.csv'"""
		f = open(output_path, 'w')
		valid_input_modes = []
		for k, v in best.items():
			valid_input_modes.append(v['input_mode'])
		for k, v in result.items():
			if k not in valid_input_modes:
				continue
			f.write(k+'\n')
			f.write(','.join(list(map(str, v)))+'\n')
		f.close()

		f = open(output_path_std, 'w')
		for k, v in n_tweets_and_std.items():
			if k not in valid_input_modes:
				continue
			f.write(k+'\n')
			f.write(','.join(list(map(str, v['n_tweets'])))+'\n')
			f.write(str(v['std'])+'\n\n')
		#json.dump(n_tweets_and_std, f)
		f.close()

		f = open(output_path_best, 'w')
		for k, v in best.items():
			if v['param'] is not None:
				f.write(k+'\n')
				f.write(str(v['param'])+'\n')
				f.write(str(v['mean'])+'\n')
		f.close()


if __name__ == "__main__":

	sum_perfo()
