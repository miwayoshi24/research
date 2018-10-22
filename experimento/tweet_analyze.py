# coding:utf-8
#!/usr/bin/env python
import MeCab
import pymongo, io, sys, os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import string
from collections import OrderedDict
from collections import Counter


def analize_tweets(place, outfile):
	try:
		con= pymongo.MongoClient(host='localhost', port=27017)
	except ConnectionFailure as e:
		sys.stderr.write("No se puede conectar a MongoDB: %s" % e)
		sys.exit()
	print('Connected Successfuly.')
	db = con.GeoTweets
	collection = db["geo_0530"]
	tweets_iterator = collection.find({"place.full_name": {'$regex': place}})
	f1 = open(outfile, "w", encoding="'utf_8-sig")
	cnt = 0

	for tweet in tweets_iterator:
		cnt+=1
		print(tweet['text'])
		if "http" in tweet['text']:
			print("This tweet incldes http")
		elif "@" in tweet['text']:
			print("This tweet incldes @")
		elif "RT" in tweet['text']:
			print("This tweet incldes RT")
		else:
			f1.write(tweet['text']+"\n")

	print("tweet found: "+ str(cnt) +"\n")
	f1.close()


def mecab_analysis2(text):
	t = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
	t.parse('')
	node = t.parseToNode(text) 
	print(node)
	output = []
	while node:
		print("entro aqui")
		if node is None:
			break
		word_type = node.feature.split(",")[0]
		if word_type in ["形容詞", "動詞","名詞", "副詞"]:
			output.append(node.surface)
		node = node.next
		
	return output

def mecab_analysisoriginal(text):
	t = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
	t.parse('')
	node = t.parseToNode(text) 
	print(node)
	output = []
	while node:
		if node.surface != "":  # ヘッダとフッタを除外
			print("entro aqui")
			word_type = node.feature.split(",")[0]
			if word_type in ["形容詞", "動詞","名詞", "副詞"]:
				output.append(node.surface)
		node = node.next
		if node is None:
			break
	return output

def count_csv(infile, outfile):
    text= str(open(infile,"r",encoding="utf-8").read())
    f1 = open(outfile, "w", encoding="'utf_8-sig")

    words = mecab_analysisoriginal(text)
# 2.集計して
    counter = Counter(words)
# 3.出力します
    for word, count in counter.most_common():
        if len(word) > 5:
            print ("%s,%d" % (word, count))
            f1.write("%s,%d" % (word, count))
            f1.write("\n")

    f1.close()



def printResult(infile):
	t = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
	fin = open(infile, 'r')
	print(t.parse(fin.read()))
	fin.close()




if __name__ == '__main__':
	place_analize = "newyork.txt"
	analize_tweets("New York", place_analize)
	count_csv(place_analize, "newyork_used_words.txt")

	

