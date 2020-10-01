#! /usr/bin/env python2
import os
import sys
import requests
import csv
import json
import copy
from shashModule import printValidValsMapDecorator
from shashModule import prettyJsonPrinter
from shashModule import jsonWriter
from shashModule import getLinesWithPattern
from shashModule import getJson
from shashModule import prettySheetPrinter

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/pint_homerun/config/'
RANK_PROFILE_EXP_PATH = MASSMEDIA_PATH + 'experiments/'
RANK_PROFILE_COMMON_PATH = MASSMEDIA_PATH + 'searchdefinitions'
RP_ACTIVE_JSON_PATH = 'files/endpoints/rankProfilesPint.json'
SD_PATHS = []
SD_PATHS_DICT = {}
RANK_PROFILE = 'rank-profile'
INHERITS = 'inherits'
DOT = '.'
CA = 'ca'
OFFNET = 'offnet'
TODAY = 'today'
CLUSTER = 'cluster'
NEWS = 'news'
CARD = 'card'
DEFAULT = 'default'
FORWARD_SLASH = '/'
SD_SUFFIX = '.sd'
FLOWER_BRACE_OPENING = '{'
DASH = '---------------------------------------------------------------------------------------------'

"""
Arguments:
Sample folderTuple:
('/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/pint_homerun/config/experiments/pint_zh_hant_hk_phrases_gbdt_v2', [], ['pint_zh_hant_hk_phrases_gbdt_v2.experiment', 'pint_zh_hant_hk_phrases_gbdt_v2_rank.sd.template', 'hongkong.gbdt.expression'])

Returns:
path for sd file as shown below:
/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/pint_homerun/config/experiments/pint_zh_hant_hk_phrases_gbdt_v2/pint_zh_hant_hk_phrases_gbdt_v2_rank.sd.template
"""
def getSdPath(folderTuple):
	sdFiles = filter(lambda string: SD_SUFFIX in string, folderTuple[2])
	sdFilePaths = []
	for sdFile in sdFiles:
		sdFilePaths.append(folderTuple[0] + FORWARD_SLASH + sdFile)
	return sdFilePaths

"""
get sd name for the given sd file path
"""
def getSd(path):
	return path.split(FORWARD_SLASH)[-1].split(DOT)[0]

"""
get all search definition paths and file names and save it in
SD_FILES dict in the format {name: path}

INFO:
sd files in RANK_PROFILE_EXP_PATH must start with 'pint_' or 'base'
"""
def initSdPaths():
	global SD_PATHS
	global SD_PATHS_DICT
	#Going through sd files in RANK_PROFILE_EXP_PATH
	for i, folderTuple in enumerate(os.walk(RANK_PROFILE_EXP_PATH)):
		if i!=0:
			SD_PATHS.extend(getSdPath(folderTuple))
	
	#Going through sd files in RANK_PROFILE_COMMON_PATH
	sdFilesCommon = getSdPath(next(os.walk(RANK_PROFILE_COMMON_PATH)))
	SD_PATHS.extend(sdFilesCommon)
	
	#Create SD_PATHS_DICT out of SD_PATHS
	SD_PATHS_DICT = {path: getSd(path) for path in SD_PATHS}

"""
Example:
Takes: rank-profile localNews inherits fresh {
Returns: (localNews, fresh) 
"""
def getRpParentTuple(line):
	words = line.split()
	return words[1], words[3].strip(FLOWER_BRACE_OPENING)

"""
Returns rank-profiles in each sd in following pattern
"ca": {"rank-profile-child": "rank-profile-parent",
       ...}
"cluster": { ... }
"""
def getSdRp():
	rankProfiles = {}
	for filePath in SD_PATHS_DICT:
		rankProfiles[SD_PATHS_DICT[filePath]] = dict(map(lambda line: getRpParentTuple(line)
							, getLinesWithPattern(filePath, RANK_PROFILE, INHERITS)))
	return rankProfiles

def getFlattenedActiveRps(activeRps):
	rps = set()
	for ep in activeRps:
		for bucket in activeRps[ep]:
			map(lambda v: rps.add(v), activeRps[ep][bucket].values())
	return rps

"""
Given a set and 2 values, it adds both of them to the set
"""
def addKeyValue(setx, v1, v2):
	setx.add(v1)
	setx.add(v2)

def getFlattenedRps(sdRps):
	rps = set()
	for sd in sdRps:
		for k, v in sdRps[sd].iteritems():
			addKeyValue(rps, k, v)
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
@printValidValsMapDecorator
def getRankProfilesForEndpoints():
	initSdPaths()
	sdRankProfiles = getSdRp()
	activeRankProfiles = getJson(RP_ACTIVE_JSON_PATH)
	activeRpInSd = getActiveRpInSd(sdRankProfiles, activeRankProfiles)
	print "AbondondedRps: ", activeRpInSd[2]
	print DASH
	print "Unused rank-profiles: ", activeRpInSd[1]
	print DASH
	return activeRpInSd[0]

def main():
	getRankProfilesForEndpoints()

if __name__ == '__main__':
	main()
