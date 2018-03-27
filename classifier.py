import pymongo, io, sys, os
from sklearn.metrics.pairwise import rbf_kernel,check_pairwise_arrays
from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import GaussianNB,MultinomialNB
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
import numpy as np
from scipy import sparse
from scipy.sparse import *
from sklearn import preprocessing
import traceback
import csv
import MeCab
import re
import pickle
import datetime
import math
mecab = MeCab.Tagger('-d /usr/share/mecab/dic/ipadic')
mecab.parse('')
from collections import Counter
from collections import defaultdict
from gensim import corpora, matutils,models
from itertools import chain
from pymongo.errors import ConnectionFailure
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.metrics import classification_report, accuracy_score
import random
import json
import time
import matplotlib.pyplot as plt

class Corpus:
	def __init__(self, db, area):
		self.db = db
		self.area = area
		if area == 'tsukuba':
			self.name_ja = u'つくば'
			self.name_en = u'Tsukuba'
			self.train_include = db.t_train2
			self.train_exclude = db.s_train2
			self.test_include = db.t_test2
			self.test_exclude = db.s_test2
		elif area == 'tokyo_23':
			self.name_ja = u'東京'
			self.name_en = u'Tokyo'
			self.sub_ja = u'区'
			self.sub_en = u'-ku'
			self.train_include = db.train_include_tokyo_23
			self.train_exclude = db.train_exclude_tokyo_23
			self.test_include = db.test_include_tokyo_23
			self.test_exclude = db.test_exclude_tokyo_23
		elif area == 'kyoto_city':
			self.name_ja = u'京都'
			self.name_en = u'Kyoto'
			self.sub_ja = u'区'
			self.sub_en = u'-ku'
			self.train_include = db.train_include_kyoto_city
			self.train_exclude = db.train_exclude_kyoto_city
			self.test_include = db.test_include_kyoto_city
			self.test_exclude = db.test_exclude_kyoto_city
		elif area == 'yokohama':
			self.name_ja = u'横浜'
			self.name_en = u'Yokohama'
			self.train_include = db.train_include_yokohama
			self.train_exclude = db.train_exclude_yokohama
			self.test_include = db.test_include_yokohama
			self.test_exclude = db.test_exclude_yokohama
		elif area == 'ibaraki':
			self.name_ja = u'茨城'
			self.name_en = u'Ibaraki'
			self.train_include = db.train_include_ibaraki
			self.train_exclude = db.train_exclude_ibaraki
			self.test_include = db.test_include_ibaraki
			self.test_exclude = db.test_exclude_ibaraki
		elif area == 'tokyo':
			self.name_ja = u'東京'
			self.name_en = u'Tokyo'
			self.train_include = db.train_include_tokyo
			self.train_exclude = db.train_exclude_tokyo
			self.test_include = db.test_include_tokyo
			self.test_exclude = db.test_exclude_tokyo
		elif area == 'kyoto':
			self.name_ja = u'京都'
			self.name_en = u'Kyoto'
			self.train_include = db.train_include_kyoto
			self.train_exclude = db.train_exclude_kyoto
			self.test_include = db.test_include_kyoto
			self.test_exclude = db.test_exclude_kyoto
		elif area == 'kanagawa':#以下(if area == kana)を参照
			self.name_ja = u'神奈川'
			self.name_en = u'Kanagawa'
			self.train_include = db.train_include_kanagawa
			self.train_exclude = db.train_exclude_kanagawa
			self.test_include = db.test_include_kanagawa
			self.test_exclude = db.test_exclude_kanagawa
		elif area == 'kana':#***神奈川県から発信されたツイートのジオタグは神奈となっている（Twitter APIのバグ）
			self.name_ja = u'神奈'
			self.name_en = u'Kanagawa'
			self.train_include = db.train_include_kana
			self.train_exclude = db.train_exclude_kana
			self.test_include = db.test_include_kana
			self.test_exclude = db.test_exclude_kana

	def corpus(self, contents, part):
		ret = []
		f = open('../data/en_stop.txt', 'r')
		data = f.read()
		f.close()
		stoplist = data.split('\n')
		for k, content in contents.items():
			#print(content)
			ret.append(self.removeStoplist(self.get_words_main(content, part), stoplist))
		return ret

	def removeStoplist(self, text, stoplist):
		stoplist_removed = []
		for word in text:
			if word not in stoplist:
				stoplist_removed.append(word)
		#print(stoplist_removed)
		return stoplist_removed

	def get_words_main(self, content, part):
		list = []
		for token in self.tokenize(content, part):
			try:
				#w = token.decode('utf-8')
				w = token
				list.append(w)
			except:
				pass
		return list

	def tokenize(self, text, part):
		#node = mecab.parseToNode(self.corpus_filter(text.encode('utf-8')))
		node = mecab.parseToNode(self.corpus_filter(text))
		while node:
			#if(node.feature.split(',')[0]=='名詞' and node.feature.split(",")[1] in ['一般','固有名詞'] and node.feature.split(",")[2] in ['地域']):
			#if(node.feature.split(',')[0]=='名詞' and node.feature.split(",")[1] in ['一般','固有名詞']) or node.feature.split(',')[0]=='形容詞' or node.feature.split(',')[0]=='動詞':
			#if node.feature.split(',')[0]=='名詞' and node.feature.split(",")[1] in ['一般','固有名詞']:
			if part == 'all':
				if node.feature.split(',')[0] != '記号':
					yield node.surface.lower()
			elif part == 'noun_verb_adjective':
				if (node.feature.split(',')[0] == '名詞' and node.feature.split(",")[1] in ['一般','固有名詞']) or node.feature.split(',')[0]=='形容詞' or node.feature.split(',')[0]=='動詞':
					yield node.surface.lower()
			elif part == 'noun':
				if node.feature.split(',')[0] == '名詞':# and node.feature.split(",")[1] in ['一般','固有名詞']:
					yield node.surface.lower()
			node = node.next

	def corpus_filter(self, text):
		#print(text)
		split_text = text.split()
		#print(split_text)
		for t in split_text[:]:
			regexp = re.compile(r'\A[\x00-\x7f]*\Z')
			result = regexp.search(t)
			if t[0] == "@" and result != None:
				#print('pass through')
				split_text.remove(t)
			elif 'http' in t:
				split_text.remove(t)
			#print('all')
		text_filtered = " ".join(split_text)
		return text_filtered


	def count_words(self, w_list):
		#単語の出現回数カウント
		w_dic = defaultdict(int)
		for i in range(len(w_list)):
			tweet = list(set(w_list[i]))
			for word in tweet:
				w_dic[word] += 1
		return w_dic


	def make_wordslist(self, f, contents):
		ret = []
		for text in contents:
			list = []
			for word in text:
				if word in f:
					list.append(word)
			ret.append(list)
		return ret

	def get_tweets(self, collection, part):
		tweets = {}
		count = 0
		#for tweet in collection.find(timeout=False):
		for tweet in collection.find():
			tweets[count] = tweet[u'text']
			count += 1
		return self.corpus(tweets, part)

	def get_tweets_test(self, id, collection, TimeWindow):
		tweets = {}
		num = 0

		tweet_data = collection.find({u'_id':id})
		tweet_list = tweet_data[0][u'text_list']

		for tweet in tweet_list:
			tweets[num] = " ".join(tweet)
			num += 1
		#print(tweets)
		return self.corpus(tweets)

	def train_clf(self, clf_str, clf_param, part):
		tweets_inside = self.get_tweets(self.train_include, part)
		tweets_outside = self.get_tweets(self.train_exclude, part)
		tweets_inside = tweets_inside + self.get_tweets(self.test_include, part)
		tweets_outside = tweets_outside + self.get_tweets(self.test_exclude, part)
		random_indices_inside = list(range(len(tweets_inside)))
		random_indices_outside = list(range(len(tweets_outside)))
		random.shuffle(random_indices_inside)
		random.shuffle(random_indices_outside)
		f = open('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/random_indices_'+self.area+'_'+clf_str+'_'+str(clf_param)+'_'+part+'.json', 'w')
		json.dump({'inside': random_indices_inside, 'outside': random_indices_outside}, f)
		f.close()
		shuffled_tweets_inside = []
		for rnd_i in random_indices_inside:
			shuffled_tweets_inside.append(tweets_inside[rnd_i])
		shuffled_tweets_outside = []
		for rnd_i in random_indices_outside:
			shuffled_tweets_outside.append(tweets_outside[rnd_i])
		self.tweets_inside = shuffled_tweets_inside
		self.tweets_outside = shuffled_tweets_outside
		tweets_inside = self.tweets_inside[:-3000]
		tweets_outside = self.tweets_outside[:-3000]
		all_tweets = tweets_inside + tweets_outside
		self.n_tweets_train = len(all_tweets)
		all_labels = [1]*len(tweets_inside) + [0]*len(tweets_outside)
		dictionary = corpora.Dictionary(all_tweets)
		dictionary.filter_extremes(no_below=10, no_above=0.5)
		#dictionary.save_as_text('dictionary_'+self.area+'_17000_adjective_verb.txt')
		#dictionary.save_as_text('dictionary_'+self.area+'_17000_noun.txt')
		#dictionary.save_as_text('dictionary_'+self.area+'_city_17000_'+part+'.txt')
		if not os.path.isdir('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/dictionary'):
			try:
				os.mkdir('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/dictionary')
			except Exception as e:
				print(str(e))
		dictionary.save_as_text('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/dictionary/dictionary_' + self.area + '_' + str(self.n_tweets_train) + '_' + part + '_' + clf_str + '_' + str(clf_param) + '.txt')
		self.dictionary = dictionary
		#dictionary = corpora.Dictionary(tweets_inside)
		#dictionary.filter_extremes(no_below=10, no_above=0.5)
		#dictionary.save_as_text(argvs[1])

		#dictionary = corpora.Dictionary(tweets_outside)
		#dictionary.filter_extremes(no_below=10, no_above=0.5)
		#dictionary.save_as_text(argvs[2])

		#F_kl = Cal_KL(tweets_inside,tweets_outside)
		#features = F_kl.run()
		#all_t = self.make_wordslist(features,tweets_inside+tweets_outside)
		# no_berow: 使われてる文章がno_berow個以下の単語無視
		# no_above: 使われてる文章の割合がno_above以上の場合無視
		#dictionary.save_as_text(argvs[1])

		#dictionary = corpora.Dictionary.load_from_text(argvs[1])
		"""
		bow_list_train = sparse.lil_matrix((len(all_t),len(dictionary)))
		row=0
		for word in all_t:
			bow_list_train[row] = list(matutils.corpus2dense([dictionary.doc2bow(word)], num_terms=len(dictionary)).T[0])
			row = row+1
		"""

		bow_list_train = []
		for tweet in all_tweets:
			#d = dictionary.doc2bow(word)
			d = list(matutils.corpus2dense([dictionary.doc2bow(tweet)], num_terms=len(dictionary)).T[0])
			bow_list_train.append(d)
		labels_train = all_labels
		"""
		num_topics = 1500
		lsi_model = models.LsiModel(bow_list_train, num_topics=num_topics)
		lsi_docs = {}
		for i, v in enumerate(bow_list_train):
			lsi_docs[i] = lsi_model[v]
			d = list(matutils.corpus2dense([lsi_docs[i]], num_terms=num_topics).T[0])
			bow_list_train[i] = d
		"""
		if clf_str == 'naive_bayes':
			classifier = MultinomialNB(alpha = clf_param['alpha'])
		elif clf_str == 'svm':
			classifier = SVC(kernel='rbf', gamma=clf_param['gamma'], C=clf_param['C'], probability=True, cache_size=clf_param['cache_size'])
		elif clf_str == 'knn':
			classifier = KNeighborsClassifier(clf_param['k'], weights=clf_param['weights'])
		elif clf_str == 'random_forest':
			classifier = RandomForestClassifier(max_depth=clf_param['max_depth'], n_estimators=clf_param['n_estimators'])#, random_state=0)

		#classifier = SVC(kernel='linear')
		#classifier = SVC(kernel='rbf')
		classifier.fit(bow_list_train, labels_train)
		if not os.path.isdir('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/model'):
			try:
				os.mkdir('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/model')
			except Exception as e:
				print(str(e))
		joblib.dump(classifier, '/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/model/' + clf_str + '_' + self.area + '_' + str(self.n_tweets_train) + '_' + part + '_' + str(clf_param)+'.pkl')
		self.classifier = classifier
		print('trained')

		return classifier

	def test_clf(self, clf_str, clf_param, part):
		#tweets_inside = self.get_tweets(self.test_include,part)
		#tweets_outside = self.get_tweets(self.test_exclude,part)
		tweets_inside = self.tweets_inside[-3000:]
		tweets_outside = self.tweets_outside[-3000:]
		all_tweets = tweets_inside + tweets_outside
		all_labels = [1]*len(tweets_inside) + [0]*len(tweets_outside)
		#print(list_include)

		dictionary = self.dictionary#corpora.Dictionary.load_from_text('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/dictionary/dictionary_' + self.area + '_' + str(self.n_tweets_train) + '_' + part + '.txt')
		bow_list_test = []
		for tweet in all_tweets:
			d = list(matutils.corpus2dense([dictionary.doc2bow(tweet)], num_terms=len(dictionary)).T[0])
			#print(len(d))
			bow_list_test.append(d)
			#print(len(d))
		labels_test = all_labels

		#classifier = joblib.load('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/model/'+clf_str + '_' + self.area + '_' + str(self.n_tweets_train) + '_' + part + '_' + str(clf_param) + '.pkl')
		output_prob = self.classifier.predict_proba(bow_list_test)
		output = self.classifier.predict(bow_list_test)

		for i_, p in enumerate(output_prob):
			output_prob[i_] = p[1]

		#print('mean squared error:'+str(squared_error/len(output_prob)))
		#output = classifier.predict(words_test)
		#corpus_obj.perT_test_vector(Clf_1,user_list,col_user,int(total_W))
		# なんか適当に保存
		#co.insert_one({"test": 3})
		#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
		#print('param: '+ str(clf_param_list[i]))

		report = classification_report(labels_test, output)
		print('area: ' + self.area + ', classifier: ' + clf_str + ', params: ' + str(clf_param) + ', part: ' + part)
		print(report)
		f = open('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/classification_report_' + self.area + '_' + clf_str + '_' + part + '.txt', 'a')
		f.write('area: ' + self.area + ', classifier: ' + clf_str + ', params: ' + str(clf_param) + ', part: ' + part + '\n')
		f.write(report)
		f.write('\n')
		f.close()
		"""
		num =  len(np.where(label_test==1)[0])
		print(num)
		num =  len(np.where(label_test==0)[0])
		print(num)
		num =  len(np.where(output==1)[0])
		print(num)
		num =  len(np.where(output==0)[0])
		print(num)
		fig = plt.figure()
		ax = fig.add_subplot(1,1,1)

		ax.hist(output_prob, bins=100)
		ax.set_title('histogram')
		ax.set_xlabel('prob')
		ax.set_ylabel('freq')
		fig.savefig('clf_dist_'+self.area+'.png')"""

	def test_clf_proba(self, clf_str, clf_param, part):
		tweets_inside = self.get_tweets(self.train_include, part)
		tweets_outside = self.get_tweets(self.train_exclude, part)
		tweets_inside = tweets_inside + self.get_tweets(self.test_include, part)
		tweets_outside = tweets_outside + self.get_tweets(self.test_exclude, part)
		f = open('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/random_indices_'+self.area+'_'+clf_str+'_'+str(clf_param)+'_'+part+'.json', 'r')
		random_indices = json.load(f)
		f.close()
		shuffled_tweets_inside = []
		for rnd_i in random_indices['inside']:
			shuffled_tweets_inside.append(tweets_inside[rnd_i])
		shuffled_tweets_outside = []
		for rnd_i in random_indices['outside']:
			shuffled_tweets_outside.append(tweets_outside[rnd_i])
		tweets_inside = shuffled_tweets_inside[-3000:]
		tweets_outside = shuffled_tweets_outside[-3000:]
		self.n_tweets_train = len(shuffled_tweets_inside[:-3000]) + len(shuffled_tweets_outside[:-3000])
		all_tweets = tweets_inside + tweets_outside
		all_labels = [1]*len(tweets_inside) + [0]*len(tweets_outside)
		#print(list_include)

		dictionary = corpora.Dictionary.load_from_text('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/dictionary/dictionary_' + self.area + '_' + str(self.n_tweets_train) + '_' + part + '_' + clf_str + '_' + str(clf_param) + '.txt')
		bow_list_test = []
		for tweet in all_tweets:
			d = list(matutils.corpus2dense([dictionary.doc2bow(tweet)], num_terms=len(dictionary)).T[0])
			#print(len(d))
			bow_list_test.append(d)
			#print(len(d))
		labels_test = all_labels

		classifier = joblib.load('/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/model/' + clf_str + '_' + self.area + '_' + str(self.n_tweets_train) + '_' + part + '_' + str(clf_param)+'.pkl')
		output_prob = classifier.predict_proba(bow_list_test)
		#output = self.classifier.predict(bow_list_test)
		squared_error = []
		for i_, p in enumerate(output_prob):
			#output_prob[i_] = p[1]
			#print(p)
			squared_error.append((labels_test[i_] - p[1])**2)

		#print('mean squared error:'+str(squared_error/len(output_prob)))
		#output = classifier.predict(words_test)
		#corpus_obj.perT_test_vector(Clf_1,user_list,col_user,int(total_W))
		# なんか適当に保存
		#co.insert_one({"test": 3})
		#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
		#print('param: '+ str(clf_param_list[i]))

		print('area: ' + self.area + ', classifier: ' + clf_str + ', params: ' + str(clf_param) + ', part: ' + part)
		print('Mean Squared Error: ' + str(sum(squared_error)/len(squared_error)))


def make_classifier():
	f = open('exp_setting.json', 'r')
	setting = json.load(f)
	f.close()
	areas = setting['areas']
	part = setting['clf']['part']
	clf_str = setting['clf']['clf_str']
	clf_param_list = setting['clf']['clf_params']

	try:
		con= pymongo.MongoClient(host='localhost', port=27017)
	except ConnectionFailure as e:
		sys.stderr.write("MongoDBへ接続できません: %s" % e)
		sys.exit()
	print('Connected Successfuly.')
	db = con.Tweets

	for area in areas:
		corpus_obj = Corpus(db, area)
		for clf_param in clf_param_list:
			clf = corpus_obj.train_clf(clf_str=clf_str, clf_param=clf_param, part=part)
			corpus_obj.test_clf(clf_str=clf_str, clf_param=clf_param, part=part)


if __name__ == '__main__':
	make_classifier()
