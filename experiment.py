import json
import traceback
import pymongo
import csv
import random
import datetime
#import matplotlib.pyplot as plt
import numpy as np
import math, sys, os, traceback
from operator import add
from collections import defaultdict
from pymongo.errors import ConnectionFailure
import time

def categorical_draw(probs):
	z = random.random()
	cum_prob = 0.0
	for i, v in probs.items():
		cum_prob += v
		if cum_prob > z:
			return i
	#最後のアームを返す
	return i

def get_follow_users_by_epsilon_greedy(i, gamma, ep, K, area, follow_list_to_calc, reward_list_to_calc, user_list):
	user_dic = {}
	total = 0
	followed_just_before = []
	flag_followed_just_before = {}
	for user_id in user_list:
		id = user_id
		flag_followed_just_before[id] = False
		try:
			follow_list_to_calc[id]
			reward = reward_list_to_calc[id]
			follow = follow_list_to_calc[id]
			nt = 0
			if follow[-1] == i-1:
				flag_followed_just_before[id] = True
				followed_just_before.append(id)
			xt = 0
			for j, i_follow in enumerate(follow):
				xt += gamma**(i-i_follow)*reward[j]
				nt += gamma**(i-i_follow)
			user_dic[id] = xt*(1.0/nt)
			if flag_followed_just_before[id]:
				total += user_dic[id]
		except Exception:
			user_dic[id] = 0

	user_list = sorted(user_dic.items(), key=lambda x:x[1])
	len_user_list = len(user_list)

	follow_list = []

	#ε-greedy
	flag_followed_next = {}
	for j in range(K):
		rand = random.random()
		#print(rand)
		if i == 0:
			rand = ep
		if rand > ep:
			#best
			v = user_list[-1][1]
			n_same_reward = 1
			for i_from_back in range(2, len_user_list):
				try:
					if user_list[-i_from_back][1] != v:
						n_same_reward = i_from_back - 1
						break
				except Exception:
					n_same_reward = len(user_list)
					break
			user = user_list.pop(-1*(int(random.random()*n_same_reward + 1)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1
		else:
			#random
			user = user_list.pop(int(random.random()*(len_user_list-j)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1

	return follow_list, flag_followed_next

def get_follow_users_by_statistics(i,gamma, K, area, prepared_period, follow_list_to_calc, reward_list_to_calc, user_list):
	user_dic = {}
	total = 0
	followed_just_before = []
	flag_followed_just_before = {}
	for user_id in user_list:
		id = user_id
		flag_followed_just_before[id] = False
		try:
			follow_list_to_calc[id]
			reward = reward_list_to_calc[id]
			follow = follow_list_to_calc[id]
			nt = 0
			if follow[-1] == i-1:
				flag_followed_just_before[id] = True
				followed_just_before.append(id)
			xt = 0
			for j, i_follow in enumerate(follow):
				xt += gamma**(i-i_follow)*reward[j]
				nt += gamma**(i-i_follow)
			user_dic[id] = xt*(1.0/nt)
			if flag_followed_just_before[id]:
				total += user_dic[id]
		except Exception:
			user_dic[id] = 0

	user_list = sorted(user_dic.items(), key=lambda x:x[1])
	len_user_list = len(user_list)

	follow_list = []

	flag_followed_next = {}
	for j in range(K):
		if i >= prepared_period:
			#best
			v = user_list[-1][1]
			n_same_reward = 1
			for i_from_back in range(2, len_user_list):
				try:
					if user_list[-i_from_back][1] != v:
						n_same_reward = i_from_back - 1
						break
				except Exception:
					n_same_reward = len(user_list)
					break
			user = user_list.pop(-1*(int(random.random()*n_same_reward + 1)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1
		else:
			#random
			user = user_list.pop(int(random.random()*(len_user_list-j)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1

	return follow_list, flag_followed_next

def get_follow_users_by_epsilon_alpha_greedy_static(i, gamma, epsilon_plus_alpha, alpha_rate, K, following, blacklist, area, follow_list_to_calc, reward_list_to_calc, user_list):
	user_dic = {}
	total = 0
	followed_just_before = []
	flag_followed_just_before = {}
	for user_id in user_list:
		id = user_id
		flag_followed_just_before[id] = False
		try:
			follow_list_to_calc[id]
			reward = reward_list_to_calc[id]
			follow = follow_list_to_calc[id]
			nt = 0
			if follow[-1] == i-1:
				flag_followed_just_before[id] = True
				followed_just_before.append(id)
			xt = 0
			for j, i_follow in enumerate(follow):
				xt += gamma**(i-i_follow)*reward[j]
				nt += gamma**(i-i_follow)
			user_dic[id] = xt*(1.0/nt)
			if flag_followed_just_before[id]:
				total += user_dic[id]
		except Exception:
			user_dic[id] = 0

	user_list = sorted(user_dic.items(), key=lambda x:x[1])
	len_user_list = len(user_list)

	follow_list = []
	alpha = epsilon_plus_alpha * alpha_rate#alpha_rate = alpha / (alpha + epsilon)
	if i != 0:
		probs = {}
		for k, v in user_list:
			if flag_followed_just_before[k]:
				probs[k] = v/total

	flag_followed_next = {}
	for j in range(K):
		rand = random.random()
		if i == 0:
			#random
			user = user_list.pop(int(random.random()*(len_user_list-j)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1
		elif rand > epsilon_plus_alpha:
			#best
			v = user_list[-1][1]
			n_same_reward = 1
			for i_from_back in range(2, len_user_list):
				try:
					if user_list[-i_from_back][1] != v:
						n_same_reward = i_from_back - 1
						break
				except Exception:
					n_same_reward = len(user_list)
					break
			user = user_list.pop(-1*(int(random.random()*n_same_reward + 1)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1
		elif rand > alpha:
			#random
			user = user_list.pop(int(random.random()*(len_user_list-j)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1

		else:
			while True:
				user_id = categorical_draw(probs)
				try:
					following[str(user_id)]
				except Exception:
					continue
				followed_user_id = following[str(user_id)][int(random.random()*len(following[str(user_id)]))]

				try:
					flag_followed_next[followed_user_id]
					continue
				except Exception:
					pass
				follow_list.append(followed_user_id)
				flag_followed_next[followed_user_id] = 1
				user_list.pop(user_list.index((followed_user_id, user_dic[followed_user_id])))
				break

	return follow_list, flag_followed_next

def get_follow_users_by_epsilon_alpha_greedy_dynamic(i, gamma, epsilon_plus_alpha, start_alpha_rate, threshold, delta, K, following, blacklist, area, follow_list_to_calc, reward_list_to_calc, user_list):
	user_dic = {}
	total = 0
	followed_just_before = []
	flag_followed_just_before = {}
	for user_id in user_list:
		id = user_id
		flag_followed_just_before[id] = False
		try:
			follow_list_to_calc[id]
			reward = reward_list_to_calc[id]
			follow = follow_list_to_calc[id]
			nt = 0
			if follow[-1] == i-1:
				flag_followed_just_before[id] = True
				followed_just_before.append(id)
			xt = 0
			for j, i_follow in enumerate(follow):
				xt += gamma**(i-i_follow)*reward[j]
				nt += gamma**(i-i_follow)
			user_dic[id] = xt*(1.0/nt)
			if flag_followed_just_before[id]:
				total += user_dic[id]
		except Exception:
			user_dic[id] = 0

	user_list = sorted(user_dic.items(), key=lambda x:x[1])
	len_user_list = len(user_list)

	follow_list = []
	alpha = 0
	if i != 0:
		probs = {}
		for k, v in user_list:
			if flag_followed_just_before[k]:
				probs[k] = v/total
		alpha = epsilon_plus_alpha*start_alpha_rate + (i-1)*delta
		if alpha > epsilon_plus_alpha - threshold:
			alpha = epsilon_plus_alpha - threshold

	flag_followed_next = {}
	for j in range(K):
		rand = random.random()
		if i == 0:
			#random
			user = user_list.pop(int(random.random()*(len_user_list-j)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1

		elif rand > epsilon_plus_alpha:
			#best
			v = user_list[-1][1]
			n_same_reward = 1
			for i_from_back in range(2, len_user_list):
				try:
					if user_list[-i_from_back][1] != v:
						n_same_reward = i_from_back - 1
						break
				except Exception:
					n_same_reward = len(user_list)
					break
			user = user_list.pop(-1*(int(random.random()*n_same_reward + 1)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1
		elif rand > alpha:
			#random
			user = user_list.pop(int(random.random()*(len_user_list-j)))
			follow_list.append(int(user[0]))
			flag_followed_next[int(user[0])] = 1

		else:
			while True:
				user_id = categorical_draw(probs)
				try:
					following[str(user_id)]
				except Exception:
					continue
				followed_user_id = following[str(user_id)][int(random.random()*len(following[str(user_id)]))]
				try:
					flag_followed_next[followed_user_id]
					continue
				except Exception:
					pass
				follow_list.append(followed_user_id)
				flag_followed_next[followed_user_id] = 1
				user_list.pop(user_list.index((followed_user_id, user_dic[followed_user_id])))
				break
	return follow_list, flag_followed_next

def get_result_of_experiments(experiment_id, K, test_period, gamma, total_W, area, q, user_list, following, blacklist, setting):
	directory_for_follow_list = setting['directory_for_follow_list']
	mode = setting['mode']

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
			print(m)
			if p is None:
				if os.path.isfile(directory_for_follow_list+area+'/follow_list_'+area+'_'+m+'_'+str(experiment_id)+'_noun_long.csv'):
					continue
			else:
				if os.path.isfile(directory_for_follow_list+area+'/follow_list_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun_long.csv'):
					continue

			follow_list_to_calc = {}
			reward_list_to_calc = {}
			follow_list = []
			cnt_pass_using_side_info_list = []
			previous_follow = None
			rnd_rate = None
			top_follow = None

			if test_period == 'short':
				f = open('data/user_id_to_data_for_prob_' + area + '_short.json', 'r')
			elif test_period == 'long':
				f = open('data/user_id_to_data_for_prob_' + area + '_long.json', 'r')
			user_id_to_data_for_prob_dic = json.load(f)
			f.close()
			user_id_to_data_for_prob = user_id_to_data_for_prob_dic.items()
			for i in range(int(total_W)):
				print('window:'+str(i))
				start = time.time()
				sum_t = 0
				sum_f = 0
				prob_dic = {}

				if m == 'epsilon_greedy':
					time_follow, flag_followed = get_follow_users_by_epsilon_greedy(i, gamma, p['epsilon'], K, area, follow_list_to_calc, reward_list_to_calc, user_list)
				elif m == 'random':
					time_follow = random.sample(user_list, K)
				elif m == 'amount_of_tweets':
					time_follow, flag_followed = get_follow_users_by_epsilon_greedy(i, gamma, p['epsilon'], K, area, follow_list_to_calc, reward_list_to_calc, user_list)
				elif m == '6TWStatistics':
					time_follow, flag_followed = get_follow_users_by_statistics(i, gamma, K, area, 6, follow_list_to_calc, reward_list_to_calc, user_list)
				elif m == '18TWStatistics':
					time_follow, flag_followed = get_follow_users_by_statistics(i, gamma, K, area, 18, follow_list_to_calc, reward_list_to_calc, user_list)
				elif m == 'epsilon_alpha_greedy_static':#確率的にフォロー元ユーザを選択
					time_follow, flag_followed = get_follow_users_by_epsilon_alpha_greedy_static(i,gamma,p['epsilon_plus_alpha'], p['alpha_rate'],K,following,blacklist, area, follow_list_to_calc, reward_list_to_calc, user_list)
				elif m == 'epsilon_alpha_greedy_dynamic':
					time_follow, flag_followed = get_follow_users_by_epsilon_alpha_greedy_dynamic(i, gamma, p['epsilon_plus_alpha'], p['start_alpha_rate'], p['threshold'], p['delta'], K, following, blacklist, area, follow_list_to_calc, reward_list_to_calc, user_list)

				if m == 'random' or (m == '6TWStatistics' and i >= 6) or (m == '18TWStatistics' and i >= 18):
					pass
				elif m == 'amount_of_tweets':

					for user_id in flag_followed.keys():
						try:
							data = {'user_id': user_id}
							flag_followed[data['user_id']]
							reward = len(user_id_to_data_for_prob_dic[str(user_id)][i])
							try:
								follow_list_to_calc[user_id].append(i)
								reward_list_to_calc[user_id].append(reward)
							except Exception:
								follow_list_to_calc[user_id] = [i]
								reward_list_to_calc[user_id] = [reward]

						except Exception:
							continue
				else:
					for user_id, data in user_id_to_data_for_prob:
						try:
							user_id = int(user_id)
							flag_followed[user_id]
							prob = data[i]
							if len(prob) == 0:
								prob = [0]
								sum_f -= 1
							sum_t += sum(prob)
							sum_f += len(prob)-sum(prob)
							prob_dic[user_id] = prob
						except Exception:
							continue

					for user_id in flag_followed.keys():
						try:
							data = {'user_id': user_id}
							flag_followed[data['user_id']]
							prob = prob_dic[data['user_id']]
							judge_t = np.array(list(map(lambda x: q*x/sum_t, prob)))
							judge_f = np.array(list(map(lambda x: (1-q)*(1-x)/sum_f, prob)))
							reward = sum(judge_t/(judge_t+judge_f))

							try:
								follow_list_to_calc[user_id].append(i)
								reward_list_to_calc[user_id].append(reward)
							except Exception:
								follow_list_to_calc[user_id] = [i]
								reward_list_to_calc[user_id] = [reward]
						except Exception:
							continue
				follow_list.append(time_follow)
				elapsed_time = time.time() - start
				print (("elapsed_time:{0}".format(elapsed_time)) + "[sec]")

			if not os.path.isdir(directory_for_follow_list + area):
				os.makedirs(directory_for_follow_list + area)

			if p is None:
				writer_tr = csv.writer(open(directory_for_follow_list+area+'/follow_list_'+area+'_'+m+'_'+str(experiment_id)+'_noun_long.csv','w'))
			else:
				writer_tr = csv.writer(open(directory_for_follow_list+area+'/follow_list_'+area+'_'+m+'_'+str(p)+'_'+str(experiment_id)+'_noun_long.csv','w'))

			writer_tr.writerows(follow_list)

def main():
	start_exp_id = int(sys.argv[1])
	n_exp = int(sys.argv[2])
	experiment_ids = range(start_exp_id, start_exp_id + n_exp)

	f = open('exp_setting.json', 'r')
	setting = json.load(f)
	f.close()
	areas = setting['areas']
	TimeWindow = setting['TimeWindow'] #タイムウィンドウ幅（hour）
	K = setting['K'] #タイムウィンドウ幅（hour）
	test_period = setting['test_period']
	gamma = 1 #epsilon-greedyの一つのパラメタ

	try:
		con= pymongo.MongoClient(host='localhost', port=27017)
	except ConnectionFailure as e:
		sys.stderr.write("MongoDBへ接続できません: %s" % e)
		sys.exit()
	print('Connected Successfuly.')

	col_geo = con.GeoTweets.geo_0530 #q計算用ジオタグ付きツイート

	db = con.Tweets

	if test_period == 'short':
		start_point = datetime.datetime(2017,5,26,20)-datetime.timedelta(hours=9) #収集開始日時
		end_point = datetime.datetime(2017,6,4,17)-datetime.timedelta(hours=9) #終了日時
	elif test_period == 'long':
		start_point = datetime.datetime(2017,6,16,9)#-timedelta(hours=9)
		end_point = datetime.datetime(2017,7,31,0)#-timedelta(hours=9)

	#全タイムウィンドウ数
	total_W = int(math.ceil((end_point-start_point).total_seconds()/(60*60*TimeWindow))) - 1
	if test_period == 'short':
		total_W = 52
	print(total_W)

	user_list = []
	if test_period == 'short':
		f = open('data/user_list.json', 'r')
	elif test_period == 'long':
		f = open('data/user_list_long.json', 'r')
	user_list = json.load(f)
	f.close()
	print(len(user_list))

	f = open('data/blacklist.json', 'r')
	blacklist = json.load(f)
	f.close()
	for i, black in enumerate(blacklist):
		blacklist[i] = int(black)
		if blacklist[i] in user_list:
			user_list.remove(blacklist[i])
	print(len(user_list))

	if test_period == 'short':
		f = open('data/link.json', 'r')
	elif test_period == 'long':
		f = open('data/link_long.json', 'r')
	following = json.load(f)
	f.close()

	for area in areas:
		if area == 'tsukuba':
			name_ja = 'つくば'
			name_en = 'Tsukuba'
		elif area == 'tokyo_23':
			name_ja = '東京'
			name_en = 'Tokyo'
			sub_ja = '区'
			sub_en = '-ku'
		elif area == 'kyoto_city':
			name_ja = '京都'
			name_en = 'Kyoto'
			sub_ja = '区'
			sub_en = '-ku'
		elif area == 'yokohama':
			name_ja = '横浜'
			name_en = 'Yokohama'

		#CMNパラメタq決め
		count = 100000
		q_count = 0
		for tweet in col_geo.find():
			location = tweet['place']['full_name']
			if area == 'tokyo_23' or area == 'kyoto_city':
				if (name_ja in location and sub_ja in location) or (name_en in location and sub_en in location):
					q_count += 1
				count -= 1
				if count == 0:
					break
			else:
				if name_ja in location or name_en in location:
					q_count += 1
				count -= 1
				if count == 0:
					break
		q = float(q_count)/100000
		print(q)

		for experiment_id in experiment_ids:
			print('exp: ' + str(experiment_id))
			print(area)

			try:
				get_result_of_experiments(experiment_id, K, test_period, gamma, total_W, area, q, user_list, following, blacklist, setting)
			except Exception as e:
				print(e)
				ex, ms, tb = sys.exc_info()
				print("\nex -> \t",type(ex))
				print(ex)
				print("\nms -> \t",type(ms))
				print(ms)
				print("\ntb -> \t",type(tb))
				print(tb)

				print("\n=== and print_tb ===")
				traceback.print_tb(tb)

if __name__ == "__main__":
	main()
