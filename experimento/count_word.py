#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import map_reduce
import re

#function to map 
def mapear(key,value):
  return [(word,1) for word in 
          remove_special_char(value.lower()).split()]

#remove special characters from the text 
def remove_special_char(s):
  return re.sub(r'[\'\_\=\?\+\*\{\}\(\)\!\‘\’\”\“\%\-\.\,\;\:]', '', s)

#function to reduce 
def reducir(inter_key,inter_value_list):
  return (inter_key,sum(inter_value_list))


#some novels 
novels = ["meguro_out.txt"]

i = {}
for filename in novels:
  f = open(filename)
  i[filename] = f.read()
  f.close()

print map_reduce.map_reduce(i,mapear,reducir)


