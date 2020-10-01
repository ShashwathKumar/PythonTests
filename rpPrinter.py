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
RANK_PROPERTIES = 'rank-properties'
MACRO = 'macro'
SUMMARY_FEATURES = 'summary-features'
OPEN_BRACE = '{'
CLOSE_BRACE = '}'
OPEN_SMALL_BRACE = '('
CLOSE_SMALL_BRACE = ')'
FUNCTION = 'function'
FIRST_PHASE = 'first-phase'
SECOND_PHASE = 'second-phase'
RANK_PROFILE = 'rank-profile'
INHERITS = 'inherits'
BASE = 'base'
SPACE = ' '
TAB = '    '

def rpPrint(rpName, rp) -> str:
	if not len(rp) > 0:
		return

	print(RANK_PROFILE + SPACE + rpName + SPACE \
		+ INHERITS + SPACE + BASE + SPACE + OPEN_BRACE)

	#sorting rank-properties based on their property name
	rankPropTuples = sorted(list(map(lambda rankProp: (rankProp.split(OPEN_SMALL_BRACE)[1].split(CLOSE_SMALL_BRACE)[0], rankProp), rp[RANK_PROPERTIES])))
	rankProps = list(map(lambda x: getRankProp(x), rankPropTuples))
	rp[RANK_PROPERTIES] = rankProps
	rankPropSumFtrPrint(rp, RANK_PROPERTIES, 1)
	print()	
	fnPrint(rp, 1)
	print()
	
	#removing rankingExpression from summary-features features
	rp[SUMMARY_FEATURES] = sorted(list(map(lambda line: line.split(OPEN_SMALL_BRACE)[1][:-1], rp[SUMMARY_FEATURES])))
	rankPropSumFtrPrint(rp, SUMMARY_FEATURES, 1)
	print()
	phasePrint(rp, FIRST_PHASE, 1)
	print()
	phasePrint(rp, SECOND_PHASE, 1)
	print(CLOSE_BRACE)

def getRankProp(tup):
	return tup[1]

def rankPropSumFtrPrint(rp, attr, tabCntDef):
	if attr not in rp:
		return

	#printing
	print(TAB*tabCntDef + attr + SPACE + OPEN_BRACE)
	for line in rp[attr]:
		print( TAB*(tabCntDef + 1) + line)
	print(TAB*tabCntDef + CLOSE_BRACE)

def fnPrint(rp, tabCntDef):
	if MACRO not in rp:
		return

	#sorting macros alphabetically
	macroList = sorted(list(rp[MACRO].items()))

	for macroName, macroContent in macroList:
		print(TAB*tabCntDef + FUNCTION + SPACE + macroName + SPACE + OPEN_BRACE)
		tabCnt = tabCntDef + 1
		for line in macroContent:
			if CLOSE_BRACE in line:
				tabCnt -= 1
			print(TAB*tabCnt + line)
			if OPEN_BRACE in line:
				tabCnt += 1
		print(TAB*tabCntDef + CLOSE_BRACE)
		print()

def phasePrint(rp, phaseName, tabCntDef):
	if phaseName in rp:
		print(phaseName + SPACE + OPEN_BRACE)
		tabCnt = tabCntDef + 1
		for line in macro:
			if CLOSE_BRACE in line:
				tabCnt -= 1
			print(TAB*tabCnt + line)
			if OPEN_BRACE in line:
				tabCnt += 1
		print(CLOSE_BRACE)
		print()
