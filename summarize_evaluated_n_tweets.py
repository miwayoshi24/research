import io, sys, os
import calendar

months = {}
for i ,v in enumerate(calendar.month_abbr):
	months[v] = i

import re
import math
import time
import datetime
import numpy as np
import json

def sum_results():
	start_exp_id = int(sys.argv[1])
	n_exp = int(sys.argv[2])
	experiment_ids = range(start_exp_id, start_exp_id + n_exp)
	f = open('exp_setting.json', 'r')
	setting = json.load(f)
	f.close()
	areas = setting['areas']

	test_period = setting['test_period']

	if test_period == 'short':
		N_TW = 52
	elif test_period == 'long':
		N_TW = 267

	path_result_dir = setting['directory_for_result_n_tweets']

	mode = setting['mode']

	now = datetime.datetime.now()

	for area in areas:
		average_n_tweets = {}
		n_tweets_and_std = {}
		best = {}
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
				reward_list = []

				if p is None:
					input_mode = m
				else:
					input_mode = m+'_'+str(p)

				for experiment_id in experiment_ids:
					if p is None:
						input_path = path_result_dir+area+'/result_n_tweets_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
					else:
						input_path = path_result_dir+area+'/result_n_tweets_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'

					if os.path.exists(input_path):
						f = open(input_path, 'r')
						for line in f:
							tmp_reward = line.strip('\n').split(',')
							if len(tmp_reward) > 1:
								tmp_reward = list(map(float, tmp_reward))
								if len(tmp_reward) < N_TW:
									print(input_path)
									print(len(tmp_reward))
									print(tmp_reward)
								reward_list.append(tmp_reward)

					else:
						print('no target file')
				if len(reward_list)==n_exp:
					reward_average = []
					n_tweets_and_std[input_mode] = {'n_tweets':[], 'std':0}
					for r in reward_list:
						n_tweets_and_std[input_mode]['n_tweets'].append(r[N_TW-1])
					n_tweets_and_std[input_mode]['std'] = np.std(np.array(n_tweets_and_std[input_mode]['n_tweets']))

					for t in range(N_TW):
						tmp_reward_average = 0
						for i in experiment_ids:
							tmp_reward_average += reward_list[i-start_exp_id][t]
						tmp_reward_average /= n_exp
						reward_average.append(tmp_reward_average)
					average_n_tweets[input_mode] = reward_average
					if m not in best:
						best[m] = {}
						best[m]['param'] = p
						best[m]['average'] = average_n_tweets[input_mode][N_TW-1]
						best[m]['input_mode'] = input_mode
					elif average_n_tweets[input_mode][N_TW-1] > best[m]['average']:
						best[m]['param'] = p
						best[m]['average'] = average_n_tweets[input_mode][N_TW-1]
						best[m]['input_mode'] = input_mode

		output_path = path_result_dir+area+'/result_'+area+'_average_n_tweets_'+now.strftime('%Y%m%d%H%M')+'.csv'
		output_path_std = path_result_dir+area+'/result_'+area+'_n_tweets_and_std_'+now.strftime('%Y%m%d%H%M')+'.csv'
		output_path_best = path_result_dir+area+'/result_'+area+'_best_param_'+now.strftime('%Y%m%d%H%M')+'.csv'

		f = open(output_path, 'w')
		valid_input_modes = []
		for k, v in best.items():
			valid_input_modes.append(v['input_mode'])
		for k, v in average_n_tweets.items():
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
		f.close()

		f = open(output_path_best, 'w')
		for k, v in best.items():
			if v['param'] is not None:
				f.write(k+'\n')
				f.write(str(v['param'])+'\n')
				f.write(str(v['average'])+'\n')
		f.close()


if __name__ == "__main__":
	sum_results()
