import pymongo, io, sys
from datetime import datetime, timedelta
import calendar
import math
import classifier
from gensim import corpora, matutils,models
import time, csv, json
from sklearn.externals import joblib

months = {}
for i ,v in enumerate(calendar.month_abbr):
	months[v] = i

client = pymongo.MongoClient('localhost', 27017)

db = client.Tweets
db2 = client.GeoTweets

#start_point = datetime(2017,5,26,20)-timedelta(hours=9) #始める日時
start_point = datetime(2017,6,16,9)#-timedelta(hours=9) #始める日時
#end_point = datetime(2017,6,4,17)-timedelta(hours=9) #終わる日時
end_point = datetime(2017,7,31,0)#-timedelta(hours=9) #終わる日時

TimeWindow = 4
#n_windows = math.ceil((l_point-t_point).total_seconds()/(60*60*TimeWindow))
n_windows = math.ceil((end_point-start_point).total_seconds()/(60*60*TimeWindow))
print(n_windows)
f = open('exp_setting.json', 'r')
setting = json.load(f)
f.close()
areas = setting['areas']
co_list = [db.tweets_per_user_long, db.tweets_per_user_long2, db.tweets_per_user_long3, db.tweets_per_user_long4]

for index, area in enumerate(areas):
	co = co_list[index]
	clf = joblib.load("/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/model/naive_bayes_" + area + "_34000_noun_{'alpha': 1}.pkl")
	dictionary = corpora.Dictionary.load_from_text("/media/nakagawa/2b0062cf-538a-43cf-b821-c79096888e06/classification/dictionary/dictionary_" + area + "_34000_noun_naive_bayes_{'alpha': 1}.txt")
	corpus_obj = classifier.Corpus(db, area)

	cnt = 0
	for data in co.find(no_cursor_timeout=True):
		cnt += 1
		print(area+': '+str(cnt))
		start = time.time()
		data['prob_list_' + area + '_noun'] = []
		for i in range(n_windows):
			data['prob_list_' + area + '_noun'].append([])
		#input_x = []
		for i, timestamp_item in enumerate(data['timestamp']):
			datetime_parts = timestamp_item.split(" ")
			time_string = datetime_parts[5] + "-" + str(months[datetime_parts[1]]) + "-" + datetime_parts[2] + " " + datetime_parts[3]
			time_tmp = datetime.strptime(time_string,'%Y-%m-%d %H:%M:%S')
			delta = time_tmp - start_point
			index = int(delta.total_seconds()/60/60/4)
			if index < 0 or index >= n_windows:
				continue
			if data['text'][i][:2] == 'RT':
				continue
			x_pred = corpus_obj.corpus({0:data['text'][i]}, 'noun')
			x_pred = list(matutils.corpus2dense([dictionary.doc2bow(x_pred[0])], num_terms=len(dictionary)).T[0])
			data['prob_list_' + area + '_noun'][index].append(clf.predict_proba([x_pred])[0][1])
		co.save(data)
		elapsed_time = time.time() - start
		print (("elapsed_time:{0} [sec]".format(elapsed_time)))
