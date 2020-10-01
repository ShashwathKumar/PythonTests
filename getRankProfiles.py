#! /usr/bin/env python3
import os
import sys
import requests
import csv
import json
import copy
from shashModule import filterEmptyValsMapDecorator
from shashModule import prettyJsonPrinter
from shashModule import jsonWriter
from shashModule import getLinesWithPattern
from shashModule import getJson
from shashModule import prettySheetPrinter

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
RANK_PROFILE_PATH = MASSMEDIA_PATH + 'homerun/config/searchdefinitions/'
RP_JSON_PATH = 'files/endpoints/rpsCode.json'
RP_PARENTS_JSON = 'files/endpoints/rpsCodeParents.json'
SD_FILES = ['ca.sd.template', 'offnet.sd.template', 'today.sd', 'card.sd', 'cluster.sd']
RANK_PROFILE = 'rank-profile'
INHERITS = 'inherits'
DOT = '.'
CA = 'ca'
OFFNET = 'offnet'
TODAY = 'today'
CLUSTER = 'cluster'
CARD = 'card'
DEFAULT = 'default'
DASH = '---------------------------------------------------------------------------------------------'

"""
Example:
Takes: rank-profile localNews inherits fresh {
Returns: (localNews, fresh) 
"""
def getRpParentTuple(line):
	words = line.split()
	return words[1], words[3]

"""
Returns rank-profiles in each sd in following pattern
"ca": {"rank-profile-child": "rank-profile-parent",
       ...}
"cluster": { ... }
"""
def getSdRp():
	rankProfiles = {}
	for fileName in SD_FILES:
		filePath = RANK_PROFILE_PATH + fileName
		rankProfiles[fileName.split(DOT)[0]] = dict(map(lambda line: getRpParentTuple(line)
							, getLinesWithPattern(filePath, RANK_PROFILE, INHERITS)))
	return rankProfiles

def getFlattenedActiveRps(activeRps):
	rps = set()
	for ep in activeRps:
		#map(lambda v: rps.add(v), list(activeRps[ep].values()))
		for v in activeRps[ep].values():
			rps.add(v)
	return rps

"""
Given a set and 2 values, it adds both of them to the set
"""
def addKeyValue(setx, v1, v2):
	setx.add(v1)
	setx.add(v2)

def getFlattenedRps(usedRps):
	rps = set()
	for sd in usedRps:
		for k, v in usedRps[sd].items():
			addKeyValue(rps, k, v)
		#map(lambda k, v: addKeyValue(rps, k, v), usedRps[sd].items())
	return rps

def getIC(rp, rpIMap):
	rpIC = [rp]
	currRp = rp
	while True:
		if currRp in rpIMap and currRp != DEFAULT:
			rpIC.append(rpIMap[currRp])
			currRp = rpIMap[currRp]
		else:
			break
	return rpIC

def getRpIC(rp, sdRps):
	for matchType in sdRps:
		if rp in sdRps[matchType]:
			return (matchType, rp, getIC(rp, sdRps[matchType]))
	return rp 

def getActiveRpInSd(sdRankProfiles, activeRankProfiles):
	sdRpMap = {}
	abondondedRps = []
	rankProfilesActive = getFlattenedActiveRps(activeRankProfiles)
	rankProfilesUsed = copy.deepcopy(rankProfilesActive) 
	rankProfilesAll = getFlattenedRps(sdRankProfiles)
	for rp in rankProfilesActive:
		rpTuple = getRpIC(rp, sdRankProfiles)
		if type(rpTuple) == tuple:
			if rpTuple[0] not in sdRpMap:
				sdRpMap[rpTuple[0]] = {rpTuple[1]: rpTuple[2]}
			else:
				sdRpMap[rpTuple[0]][rpTuple[1]] = rpTuple[2]
			rankProfilesUsed.update(rpTuple[2])
		else:
			abondondedRps.append(rpTuple)
	return (sdRpMap, rankProfilesAll - rankProfilesUsed, abondondedRps)
	
@prettySheetPrinter
@jsonWriter(fileName = RP_PARENTS_JSON)
@filterEmptyValsMapDecorator
def getRankProfilesForEndpoints():
	sdRankProfiles = getSdRp()
	activeRankProfiles = getJson(RP_JSON_PATH)
	activeRpInSd = getActiveRpInSd(sdRankProfiles, activeRankProfiles)
	print("AbondondedRps: ", activeRpInSd[2])
	print(DASH)
	print("Unused rank-profiles: ", activeRpInSd[1])
	for rp in activeRpInSd[1]:
		print(rp)
	print(DASH)
	return activeRpInSd[0]

def main():
	getRankProfilesForEndpoints()

if __name__ == '__main__':
	main()
