import io, sys, os
import calendar

months = {}
for i ,v in enumerate(calendar.month_abbr):
	months[v] = i

import math
import time
import datetime
import numpy as np
import json
from json import encoder

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

	path_result_dir = setting['directory_for_result_recall']

	mode = setting['mode']

	now = datetime.datetime.now()

	for area in areas:
		average_recall = {}
		average_recall2 = {}
		std = {}
		std2 = {}
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
				reward_list2 = []

				if p is None:
					input_mode = m
				else:
					input_mode = m+'_'+str(p)

				for experiment_id in experiment_ids:
					if p is None:
						input_path = path_result_dir+area+'/recall_accumulated_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
						input_path2 = path_result_dir+area+'/recall_'+area+'_'+m+'_'+str(experiment_id)+'_noun.csv'
					else:
						input_path = path_result_dir+area+'/recall_accumulated_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'
						input_path2 = path_result_dir+area+'/recall_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun.csv'

					if os.path.exists(input_path):
						f = open(input_path, 'r')
						for line in f:
							tmp_reward = line.strip('\n').split(',')
							if len(tmp_reward) > 1:
								tmp_reward = list(map(float, tmp_reward))
								reward_list.append(tmp_reward)

					else:
						print('no target file')

					if os.path.exists(input_path2):
						f = open(input_path2, 'r')
						for line in f:
							tmp_reward = line.strip('\n').split(',')
							if len(tmp_reward) > 1:
								tmp_reward = list(map(float, tmp_reward))
								reward_list2.append(tmp_reward)

					else:
						print('no target file')
				if len(reward_list)==n_exp:
					reward_average = []
					std[input_mode] = {'recalls':[], 'std':0}
					for r in reward_list:
						std[input_mode]['recalls'].append(r[-1])
					std[input_mode]['std'] = np.std(np.array(std[input_mode]['recalls']))

					for t in range(len(reward_list[0])):
						tmp_reward_average = 0
						for i in experiment_ids:
							tmp_reward_average += reward_list[i-start_exp_id][t]
						tmp_reward_average /= n_exp
						reward_average.append(tmp_reward_average)
						average_recall[input_mode] = reward_average

				if len(reward_list2)==n_exp:
					reward_average = []
					std2[input_mode] = {'recalls':[], 'std':0}
					for r in reward_list2:
						std2[input_mode]['recalls'].append(r[-1])
					std2[input_mode]['std'] = np.std(np.array(std2[input_mode]['recalls']))

					for t in range(len(reward_list2[0])):
						tmp_reward_average = 0
						for i in experiment_ids:
							tmp_reward_average += reward_list2[i-start_exp_id][t]
						tmp_reward_average /= n_exp
						reward_average.append(tmp_reward_average)
						average_recall2[input_mode] = reward_average


		output_path = path_result_dir+area+'/result_recall_accumulated_'+area+'_average_'+now.strftime('%Y%m%d%H%M')+'.csv'
		output_path2 = path_result_dir+area+'/result_recall_'+area+'_average_'+now.strftime('%Y%m%d%H%M')+'.csv'
		output_path_std = path_result_dir+area+'/result_recall_accumulated_'+area+'_std_'+now.strftime('%Y%m%d%H%M')+'.csv'
		output_path_std2 = path_result_dir+area+'/result_recall_'+area+'_std_'+now.strftime('%Y%m%d%H%M')+'.csv'
		f = open(output_path, 'w')
		for k, v in average_recall.items():
			f.write(k+'\n')
			f.write(','.join(list(map(str, v)))+'\n')
		f.close()

		f = open(output_path_std, 'w')
		for k, v in std.items():
			f.write(k+'\n')
			f.write(','.join(list(map(str, v['recalls'])))+'\n')
			f.write(str(v['std'])+'\n\n')
		f.close()

		f = open(output_path2, 'w')
		for k, v in average_recall2.items():
			f.write(k+'\n')
			f.write(','.join(list(map(str, v)))+'\n')
		f.close()

		f = open(output_path_std2, 'w')
		for k, v in std2.items():
			f.write(k+'\n')
			f.write(','.join(list(map(str, v['recalls'])))+'\n')
			f.write(str(v['std'])+'\n\n')
		f.close()

if __name__ == "__main__":
	sum_results()
