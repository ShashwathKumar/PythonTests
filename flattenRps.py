import os
import sys
import requests
import json
import copy
from collections import namedtuple
from typing import NamedTuple
from shashModule import getLines
from shashModule import filterEmptyValsMapDecorator
from shashModule import prettyJsonPrinter
from shashModule import jsonWriter
from shashModule import getLinesWithPattern
from shashModule import getJson
from shashModule import prettySheetPrinter
from rpPrinter import rpPrint

##By default this file works only with ca.sd.template
MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
RANK_PROFILE_PATH = MASSMEDIA_PATH + 'homerun/config/searchdefinitions/'
SD_FILE = RANK_PROFILE_PATH + 'ca.sd.template'
RANK_PROFILE = 'rank-profile'
INHERITS = 'inherits'
RANK_PROPERTIES = 'rank-properties'
MACRO = 'macro'
SPACE = ' '
SUMMARY_FEATURES = 'summary-features'
RANK_FEATURES = 'rank-features'
FIRST_PHASE = 'first-phase'
SECOND_PHASE = 'second-phase'
BASE = 'base'
OPEN_BRACE = '{'
CLOSE_BRACE = '}'
OPEN_BRACE_SPACE = ' {'
REFINED_RPS_JSON = 'files/endpoints/refinedRps.json'
RP_PROPS =      [
		RANK_PROPERTIES + OPEN_BRACE_SPACE,
		SUMMARY_FEATURES + OPEN_BRACE_SPACE,
		RANK_FEATURES + OPEN_BRACE_SPACE
		]
RP_PROPS_EXPS = [
		FIRST_PHASE + OPEN_BRACE_SPACE,
		SECOND_PHASE + OPEN_BRACE_SPACE
		]
REFINED_RPS = {} #refined rps global variable
DASH_MINI = '--------------------------------------------------'
DASH = '---------------------------------------------------------------------------------------------'

def getRankPropsFlattened(chainBeforeFlatten, chainAfterFlatten):
	rankPropsBaseSet = set(REFINED_RPS_DICT[BASE][RANK_PROPERTIES])
	rankPropsSecBase = []
	rankPropsSecBaseSet = set()

	for rp in chainBeforeFlatten[1:]: #do not iterate through base
		if len(REFINED_RPS_DICT[rp][RANK_PROPERTIES]) > 0:
			for rankProp in REFINED_RPS_DICT[rp][RANK_PROPERTIES]:
				if rankProp not in rankPropsBaseSet and rankProp not in rankPropsSecBaseSet:
					rankPropsSecBase.append(rankProp)
					rankPropsSecBaseSet.add(rankProp)
	return rankPropsSecBase

def getSumFtrsFlattened(chainBeforeFlatten, chainAfterFlatten):
	sumFtrsBaseSet = set(REFINED_RPS_DICT[BASE][SUMMARY_FEATURES])
	sumFtrsSecBase = []
	sumFtrsSecBaseSet = set()

	for rp in chainBeforeFlatten[1:]: #do not iterate through base
		if len(REFINED_RPS_DICT[rp][SUMMARY_FEATURES]) > 0:
			for sumFtr in REFINED_RPS_DICT[rp][SUMMARY_FEATURES]:
				if sumFtr not in sumFtrsBaseSet and sumFtr not in sumFtrsSecBaseSet:
					sumFtrsSecBase.append(sumFtr)
					sumFtrsSecBaseSet.add(sumFtr)

		if len(REFINED_RPS_DICT[rp][RANK_FEATURES]) > 0:
			for rankFtr in REFINED_RPS_DICT[rp][RANK_FEATURES]:
				if rankFtr not in sumFtrsBaseSet and sumFtr not in sumFtrsSecBaseSet:
					sumFtrsSecBase.append(sumFtr)
					sumFtrsSecBaseSet.add(sumFtr)
	return sumFtrsSecBase

def getMacrosFlattened(chainBeforeFlatten, chainAfterFlatten):
	#following will be list and sets of tuples
	macrosSecBase = {}

	#print(DASH)
	#print('base macros')
	#for macro in REFINED_RPS_DICT[BASE][MACRO]:
	#	print(macro)
	#print(DASH_MINI)

	#firstly remove duplicate macros
	#then if contents are different then append dup<num>
	#and add it to list

	#print('rps:')
	for rp in chainBeforeFlatten[1:]: #do not iterate through base
		#print(rp)
		for macro in REFINED_RPS_DICT[rp][MACRO]:
			#print(macro)
			if macro in REFINED_RPS_DICT[BASE][MACRO] and \
				REFINED_RPS_DICT[rp][MACRO][macro] == REFINED_RPS_DICT[BASE][MACRO][macro]:
				continue
			elif macro in macrosSecBase and \
				REFINED_RPS_DICT[rp][MACRO][macro] == macrosSecBase[macro]:
				continue
			elif macro in REFINED_RPS_DICT[BASE][MACRO] or \
				macro in macrosSecBase: #dup
				#find a dup suffix and add it
				for i in range(20): #random num for dups
					macroDup = macro + '_dup' + str(i)
					if macroDup not in macrosSecBase:
						macrosSecBase[macroDup] = REFINED_RPS_DICT[rp][MACRO][macro]
						break
					elif REFINED_RPS_DICT[rp][MACRO][macro] == macrosSecBase[macroDup]: 
						#if dup is ther check if macro matches dup
						break
					
			else:
				macrosSecBase[macro] = REFINED_RPS_DICT[rp][MACRO][macro]
		#print(DASH_MINI)

	#After that manually
	#1. you will have to check if the macros
	#are used in the eqs and delete them if they are not
	
	#print(macrosSecBase)
	#print(DASH)
	return macrosSecBase

def getFlattenedChainMap(chainBeforeFlatten, chainAfterFlatten):
	flattenedChainMap = {}

	#initializing each rp in chainAfterFlatten
	for rp in chainAfterFlatten:
		flattenedChainMap[rp] = {}

	#process rank-properties - inherited?
	rankPropsFlattened = getRankPropsFlattened(chainBeforeFlatten, chainAfterFlatten)
	#putting it only in the base of chainAfterFlatten
	flattenedChainMap[chainAfterFlatten[0]][RANK_PROPERTIES] = rankPropsFlattened

	#process summary-features and rank-features
	sumFtrsFlattened = getSumFtrsFlattened(chainBeforeFlatten, chainAfterFlatten)
	#putting it only in the base of chainAfterFlatten
	flattenedChainMap[chainAfterFlatten[0]][SUMMARY_FEATURES] = sumFtrsFlattened

	#process macros
	macrosFlattened = getMacrosFlattened(chainBeforeFlatten, chainAfterFlatten)
	flattenedChainMap[chainAfterFlatten[0]][MACRO] = macrosFlattened
	
	#process first-phase and second-phase

	return flattenedChainMap

#@prettyJsonPrinter
def getFlattenedRps() -> dict:
	global REFINED_RPS_DICT
	REFINED_RPS_DICT = getJson(REFINED_RPS_JSON)
	#chainBeforeFlatten: will have base
	chainBeforeFlatten = list(reversed(sys.argv[1].split(',')))
	#chainAfterFlatten: will not have base - it is understood
	chainAfterFlatten = list(reversed(sys.argv[2].split(',')))
	flattenedChainMap = getFlattenedChainMap(chainBeforeFlatten, chainAfterFlatten)

	#printing rank-profiles
	#print(DASH)
	for rpName in flattenedChainMap:
		rpPrint(rpName, flattenedChainMap[rpName])	
	#print(DASH)
	
	return flattenedChainMap

def main():
	getFlattenedRps()

if __name__ == "__main__":
	main()
