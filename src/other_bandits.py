def get_select_all_ucb(i,gamma, K,collection, region):
	#全部のreward Ver.
	user_dic = {}
	#for user in collection.find(timeout=False):
	total_counts = 0
	counts = {}
	for user in collection.find():
		id = user['_id']
		if user.get(u'reward_' + region) is not None:
			reward = user['reward_' + region]
			follow = user['follow_' + region]
			total_counts += len(follow)
			#counts[id] = len(follow)
			nt = 0
			for j in follow:
				nt += gamma**(i-j)
			xt = 0
			for j in range(len(follow)):
				xt += gamma**(i-follow[j])*reward[j]
			user_dic[id] = xt*(1.0/nt)
		else:
			user_dic[id] = 0
	#user_list = sorted(user_dic.items(), key=lambda x:x[1])
	#user_list = user_dic.items()
	#tmp_user_dic = user_
	follow_list = []
	#εGreedy
	#bonus = {}
	#K_cnt = 0
	for user in collection.find():
		if 'follow_' + region not in user:
			user_dic.pop(user['_id'])
			follow_list.append(int(user['_id']))
			#K_cnt += 1
			if len(follow_list) == K:
				break
		else:
			#user_dic[user['_id']] += math.sqrt((2 * math.log(total_counts)) / float(len(user['follow_' + region])))
			#user_dic[user['_id']] += math.sqrt((2 * math.log(i)) / float(len(user['follow_' + region])))
			user_dic[user['_id']] += math.sqrt((math.log(i)) / 2.0 / float(len(user['follow_' + region])))
	if K - len(follow_list) > 0:
		user_list = sorted(user_dic.items(), key=lambda x:x[1])
		for j in range(K-len(follow_list)):
			v = user_list[-1][1]
			v_count = [user_list[x][1] for x in range(len(user_list))].count(v)
			user = user_list.pop(-1*random.randint(1,v_count))
			follow_list.append(int(user[0]))
	return follow_list

def get_select_all_d_ucb(i,gamma, K,collection, region):
	#全部のreward Ver.
	user_dic = {}
	#for user in collection.find(timeout=False):
	total_counts = 0
	counts = {}
	nts = {}
	for user in collection.find():
		id = user['_id']
		if user.get(u'reward_' + region) is not None:
			reward = user['reward_' + region]
			follow = user['follow_' + region]
			total_counts += len(follow)
			#counts[id] = len(follow)
			nt = 0
			for j in follow:
				nt += gamma**(i-j-1)
			nts[id] = nt
			xt = 0
			for j in range(len(follow)):
				xt += gamma**(i-follow[j]-1)*reward[j]
			user_dic[id] = xt*(1.0/nt)
		else:
			user_dic[id] = 0

	#user_list = sorted(user_dic.items(), key=lambda x:x[1])
	#user_list = user_dic.items()
	#tmp_user_dic = user_
	follow_list = []
	#εGreedy
	#bonus = {}
	#K_cnt = 0
	gamma_all = 0
	for j in range(i):
		gamma_all += gamma ** j
	print('gamma: '+str(gamma_all))
	for user in collection.find():
		if 'follow_' + region not in user:
			user_dic.pop(user['_id'])
			follow_list.append(int(user['_id']))
			#K_cnt += 1
			if len(follow_list) == K:
				break
		else:
			#user_dic[user['_id']] += math.sqrt((2 * math.log(total_counts)) / float(len(user['follow_' + region])))
			#user_dic[user['_id']] += math.sqrt((2 * math.log(i)) / float(len(user['follow_' + region])))
			user_dic[user['_id']] += math.sqrt((2 * math.log(gamma_all)) / float(nts[int(user['_id'])]))
			#user_dic[user['_id']] += math.sqrt((math.log(i)) / 2.0 / float(len(user['follow_' + region])))
	if K - len(follow_list) > 0:
		user_list = sorted(user_dic.items(), key=lambda x:x[1])
		for j in range(K-len(follow_list)):
			v = user_list[-1][1]
			v_count = [user_list[x][1] for x in range(len(user_list))].count(v)
			user = user_list.pop(-1*random.randint(1,v_count))
			follow_list.append(int(user[0]))
	return follow_list

def categorical_draw(probs):
	z = random.random()
	#print(z)
	cum_prob = 0.0
	for i, v in probs.items():
		cum_prob += v
		if cum_prob > z:
			#print(i)
			return i
	#最後のアームを返す
	return i

def categorical_draw2(probs):
	z = random.uniform(0, 2729.217286593032)
	#print(z)
	cum_prob = 0.0
	for i, v in probs.items():
		cum_prob += v
		if cum_prob > z:
			#print(i)
			return i
	#最後のアームを返す
	return i

def get_select_all_softmax(i,gamma, K,collection, region):
	#全部のreward Ver.
	user_dic = {}
	#for user in collection.find(timeout=False):
	#total_counts = 0
	counts = {}
	temperature = 0.1
	for user in collection.find():
		id = user['_id']
		if user.get(u'reward_' + region) is not None:
			reward = user['reward_' + region]
			follow = user['follow_' + region]
			#total_counts += len(follow)
			#counts[id] = len(follow)
			nt = 0
			for j in follow:
				nt += gamma**(i-j)
			xt = 0
			for j in range(len(follow)):
				xt += gamma**(i-follow[j])*reward[j]
			user_dic[id] = xt*(1.0/nt)
		else:
			user_dic[id] = 0
	#user_list = sorted(user_dic.items(), key=lambda x:x[1])
	#user_list = user_dic.items()
	#tmp_user_dic = user_
	follow_list = []
	#εGreedy
	#bonus = {}
	#K_cnt = 0
	z = sum([math.exp(v / temperature) for v in user_dic.values()])
	probs = {}
	for i, v in user_dic.items():
		probs[i] = math.exp(v / temperature) / z
	while True:
		user_id = categorical_draw(probs)
		user_dic.pop(user_id)
		probs.pop(user_id)
		follow_list.append(user_id)
		if len(follow_list) == K:
			break

	return follow_list

def get_select_all_thompson_sampling(i,gamma, K,collection, region):
	#全部のreward Ver.
	user_dic = {}
	#for user in collection.find(timeout=False):
	#total_counts = 0
	counts = {}
	sigma = 0.1
	for user in collection.find():
		id = user['_id']
		if user.get(u'reward_' + region) is not None:
			reward = user['reward_' + region]
			follow = user['follow_' + region]
			#total_counts += len(follow)
			counts[id] = len(follow)
			nt = 0
			for j in follow:
				nt += gamma**(i-j)
			xt = 0
			for j in range(len(follow)):
				xt += gamma**(i-follow[j])*reward[j]
			user_dic[id] = xt*(1.0/nt)
		else:
			user_dic[id] = 0
			counts[id] = 0
	#user_list = sorted(user_dic.items(), key=lambda x:x[1])
	#user_list = user_dic.items()
	#tmp_user_dic = user_
	follow_list = []
	#εGreedy
	#bonus = {}
	#K_cnt = 0
	theta = []
	for i, v in counts.items():
		if v == 0:
			theta.append((i, random.uniform(0, 1)))
		else:
			theta.append((i, random.gauss(user_dic[i], sigma/math.sqrt(v))))
			#theta.append((arm, random.gauss(self.values[arm], self.sigma)))
	#theta = [(arm, random.gauss(self.values[arm], 0.1/math.sqrt(self.counts_alpha[arm]+self.counts_beta[arm]))) for arm in range(len(self.counts_alpha))]
	theta = sorted(theta, key=lambda x:x[1])

	while True:
		follow_list.append(theta[-1][0])
		theta.pop(-1)
		if len(follow_list) == K:
			break

	return follow_list
