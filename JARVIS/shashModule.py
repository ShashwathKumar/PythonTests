#!/usr/bin/env python3
import os
import sys
import requests
import csv
import json
import collections

FILENAME = 'fileName'
TAB = '\t'
DASH_MINI = '--------------------------------------------------'
DASH = '---------------------------------------------------------------------------------------------'

"""
DECORATORS
"""

'''
Accepts a map and returns a map without key-value pairs where values are empty
'''
def filterEmptyValsMapDecorator(func):
	def newFunc():
		mapx = func()
		return {k:v for k,v in mapx.iteritems() if len(v) != 0}
	return newFunc	

'''
Just prints a dict in a pretty format using json.dumps

anamolies: prettyJsonPrinter was running twice when chained before jsonWriter (don't know root cause)
'''
def prettyJsonPrinter(func):
	def newFunc():
		dictx = func()
		print(json.dumps(dictx, sort_keys=True, indent=4))
		return dictx
	return newFunc

'''
Uses recursion
UNDER DEVELOPMENT: Iterative solution is more preferred in prod env
'''
def prettyDictSheetPrint(dictx, tabCnt):
	for key in dictx:
		print(TAB * tabCnt, key)
		if type(dictx[key]) == dict:
			prettyDictSheetPrint(dictx[key], tabCnt+1)
		else:
			print(TAB * (tabCnt+1), dictx[key])
'''
Prints a dict in a format which can be easily copied and pasted in google sheet
UNDER DEVELOPMENT
'''
def prettySheetPrinter(func):
	def newFunc():
		dictx = func()
		orderedDict = collections.OrderedDict(sorted(dictx.items()))
		tabCnt = 0
		prettyDictSheetPrint(orderedDict, tabCnt)
		return dictx
	return newFunc

'''

UNDER DEVELOPMENT
'''
def prettyMapPrinter(func):
	def newFunc():
		dictx = func()
		for k,v in dictx.iteritems():
			print(k, v)
			print()
		return dictx
	return newFunc

'''
decorator with params
@reference: https://www.geeksforgeeks.org/decorators-with-parameters-in-python
'''
def jsonWriter(*args, **kwargs):
	def newFunc(func):
		dictx = func()
		fileName = kwargs[FILENAME]
		with open(fileName, 'w') as f:
			json.dump(dictx, f, ensure_ascii=False)
		return func
	return newFunc

"""
UTIL METHODS
"""

def findArgs(string, *args):
	stringSet = string.split()
	for arg in args:
		if arg not in stringSet:
			return False
	return True 

def getLines(fileName):
	with open(fileName, 'r') as f:
		return f.readlines()

def getJson(fileName):
	with open(fileName, 'r') as f:
		return json.load(f)

def getLinesWithPattern(fileName, *args):
	lines = []
	with open(fileName, 'r') as f:
		for line in f:
			if findArgs(line, *args):
				lines.append(line)
	return lines	

def printTuple(tuplex):
	for i, v in enumerate(tuplex):
		print(v)
		if(i!=len(tuplex)-1):
			print(DASH_MINI)
	print(DASH)

def printArgs(*args):
	for i, arg in enumerate(args):
		print(arg)
		if(i!=len(args)-1):
			print(DASH_MINI)
	print(DASH)

class listSet(object):
	def __init__(self):
		self.listx = []
		self.setx = set()

	def __init(self, listx):
		self.listx = []
		self.setx = set(listx)

	def add(self, val):
		self.listx.append(val)
		self.setx.add(val)

	def get(self, val):
		return val in self.setx

