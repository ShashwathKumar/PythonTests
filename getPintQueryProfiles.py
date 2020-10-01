#! /usr/bin/env python2
import os
import sys
import requests
import csv
import json
import xmltodict
import xml.etree.ElementTree as ET
import pprint
from shashModule import printValidValsMapDecorator
from shashModule import prettyMapPrinter
from shashModule import prettyJsonPrinter
from shashModule import prettySheetPrinter
from shashModule import jsonWriter
from shashModule import getLines

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
SEARCH_PATH = 'pint_homerun/src/main/application/search/'
QUERY_PROFILE_PATH = MASSMEDIA_PATH + SEARCH_PATH + 'query-profiles/'
DOC_XML_FILE = MASSMEDIA_PATH + SEARCH_PATH + 'stateless-handlers.xml'
TODAY_XML_FILE = MASSMEDIA_PATH + SEARCH_PATH + 'stateless-config.xml'
ENDPOINTS_PINT_PATH = 'files/endpoints/endpoints_pint.csv'
RANK_PROFILES_ENDPOINTS_JSON = 'files/endpoints/rankProfilesPint.json'
RANK_PROFILES_SD_JSON = 'files/endpoints/rankProfilesPintSd.json'
QUERY_PROFILES_JSON = 'files/endpoints/queryProfilesPint.json'
XML_SUFFIX = '.xml'
XML_MAGS_NODE_BEGINNING = '<config name="slingstone.searchplatform.handler.PintDigitalMagazinesBucketHandler">' 
XML_MAGS_NODE_ENDING    = '</config>'
XML_DOCS_NODE_BEGINNING = '<config name="slingstone.searchplatform.handler.PintBucketHandler">'
XML_DOCS_NODE_ENDING    = '</config>'
XML_TODAY_NODE_BEGINNING = '<config name="slingstone.serving.common.handler.TodayModuleBuckets">'
XML_TODAY_NODE_ENDING    = '</config>'
RANKING_PROFILE = 'ranking.profile'
RANK_PROFILE = 'rankProfile'
INHERITS = 'inherits'
KEY = '@key'
TEXT = '#text'
NAME = 'name'
DOCS = 'docs'
MAGZ = 'magz'
MAGS = 'mags'
TODAY = 'today'
ROGERS = 'rogers'
MARKET = 'market'
SITE = 'site'
SCREEN = 'screen'
BUCKET = 'bucket'
QPS = 'queryprofiles'
CONFIG = 'config'
ENDPOINTS = 'endpoints'
PATH = 'path'
BUCKETS = 'buckets'
DEFAULT_PROFILE = 'defaultProfile'
PROFILE = 'profile'
MARKET_CONFIG_MAP = 'marketConfigMap'
SITE_CONFIG_MAP = 'siteConfigMap'
SCREEN_CONFIG_MAP = 'screenConfigMap'
CATEGORY_CONFIG_MAP = 'categoryConfigMap'
BUCKET_CONFIG_MAP = 'bucketConfigMap'
QUERY_CONFIG = 'queryConfig'
ITEM = 'item'
PROFILE = 'profile'
queryProfileMap = {}
pp = pprint.PrettyPrinter(indent=4)
DASH = '---------------------------------------------------------------------------------------------'

def getQueryProfiles(fileName, beginning, ending):
	queryProfiles = {}
	with open(fileName, 'r') as f:
		fileContent = f.read()
		begIndex = fileContent.find(beginning)
		endIndex = fileContent.find(ending, begIndex)
		return xmltodict.parse(fileContent[begIndex: endIndex + len(ending) + 1])
	return queryProfiles

'''
Parses through an endpoint and fetches its specific attributes like market, site and bucketName it is calling
@return: a dictionary with above parsed information
'''
def endpointParser(endpoint):
	endpointInfoMap = {}
	endpointParts = endpoint.split('/')
	endpointInfoMap[MARKET] = endpointParts[4]
	endpointInfoMap[SITE] = endpointParts[3]
	endpointInfoMap[BUCKET] = endpointParts[6]
	return endpointInfoMap


'''
Parses through each endpoint in endpointParserMap and call their respective parsing logic for each kind of endpoint,
namely, mags (magazines), today (ntk), docs (rest of the docs like homerun, sports and finance)
'''
def addQps(endpointParserMap):
	for endpoint in endpointParserMap:
		if endpointParserMap[endpoint][SITE] == MAGS:
			endpointParserMap[endpoint][QPS] = getMagsQps(endpointParserMap[endpoint])
		elif endpointParserMap[endpoint][SITE] == TODAY or endpointParserMap[endpoint][SITE] == ROGERS:
			endpointParserMap[endpoint][QPS] = getTodayQps(endpoint)
		else:
			endpointParserMap[endpoint][QPS] = getDocsQps(endpointParserMap[endpoint])
	return endpointParserMap	

'''
@return: { ga: pint_en_ca_finance_caprelevance}
Following is a sample of bucketConfigMap item
{
    "@key": "ga",
    "queryConfig": {
        "item": [
            {
                "#text": "pint_en_ca_finance_caprelevance",
                "@key": "profile"
            },
            {
                "#text": "true",
                "@key": "cachable"
            }
        ]
    }
}
'''
def parseBucketConfigMapItem(item):
	bucketName = item[KEY]
	qp = ''
	for bucket in item[QUERY_CONFIG][ITEM]:
		if bucket[KEY] == PROFILE:
			qp = bucket[TEXT]
	return {str(bucketName): str(qp)} #str for converting unicode to normal string

'''
Confession: Not the most efficient way to do it, because I am iterating through the entire
config for finding the qp for every endpoint. It can be done more efficiently but it would
require more complication of code and more investment of developer's time
'''
def getMagsQps(eInfoMap):
	marketConfigList = queryProfileMap[MAGZ][CONFIG][MARKET_CONFIG_MAP][ITEM]
	qpMap = {}
	for config in marketConfigList:
		if eInfoMap[MARKET] == config[KEY]:
			#all screenConfigs are default and all categoryConfigs are finance
			bucketConfigItems = config[SITE_CONFIG_MAP][ITEM][SCREEN_CONFIG_MAP][ITEM][CATEGORY_CONFIG_MAP][ITEM][BUCKET_CONFIG_MAP][ITEM]
			map(lambda configItem: qpMap.update(parseBucketConfigMapItem(configItem)), bucketConfigItems)
			break
	return qpMap

def getTodayQps(endpoint):
	endpointItemsList = queryProfileMap[TODAY][CONFIG][ENDPOINTS][ITEM]
	qpMap = {}
	for endpointItem in endpointItemsList:
		if endpointItem[PATH] == endpoint:
			if BUCKETS in endpointItem:
				buckets = endpointItem[BUCKETS][ITEM]
				if type(buckets) == dict:
					qpMap.update({str(buckets[PROFILE]): str(buckets[PROFILE])})
				elif type(buckets) == list:
					for bucket in buckets:
						qpMap.update({str(bucket[PROFILE]): str(bucket[PROFILE])})
			else:
				qpMap.update({str(endpointItem[DEFAULT_PROFILE]): str(endpointItem[DEFAULT_PROFILE])})
			break
	return qpMap


'''
Just bucket parser for docs part of endpoints
'''
def bucketParserForDocsEps(bucketConfigItemObj, eInfoMap):
	#all screenConfigs are default
	if type(bucketConfigItemObj) == list:
		for bucketConfigItem in bucketConfigItemObj:
			if bucketConfigItem[KEY] == eInfoMap[BUCKET]:
				return parseBucketConfigMapItem(bucketConfigItem)
	else: #in which it has to be a dict
		if bucketConfigItemObj[KEY] == eInfoMap[BUCKET]:
			return parseBucketConfigMapItem(bucketConfigItemObj)
	print "Endpoint not found"
	print eInfoMap
	print DASH
	return None

def getDocsQps(eInfoMap):
	marketConfigList = queryProfileMap[DOCS][CONFIG][MARKET_CONFIG_MAP][ITEM]
	qpMap = {}
	for config in marketConfigList:
		if eInfoMap[MARKET] == config[KEY]:
			if type(config[SITE_CONFIG_MAP][ITEM]) == list:
				for siteConfigItem in config[SITE_CONFIG_MAP][ITEM]:
					if siteConfigItem[KEY] == eInfoMap[SITE]:
						bucketInfo = bucketParserForDocsEps(siteConfigItem[SCREEN_CONFIG_MAP][ITEM][BUCKET_CONFIG_MAP][ITEM], eInfoMap)
						if bucketInfo:
							qpMap.update(bucketInfo)
						break
			else: #in which case it has to be a dict
				siteConfigItem = config[SITE_CONFIG_MAP][ITEM]
				if siteConfigItem[KEY] == eInfoMap[SITE]:
					bucketInfo = bucketParserForDocsEps(siteConfigItem[SCREEN_CONFIG_MAP][ITEM][BUCKET_CONFIG_MAP][ITEM], eInfoMap)
					if bucketInfo:
						qpMap.update(bucketInfo)
					break
	return qpMap

'''
methods credits: aaronnagao
'''
def getQueryProfileInheritanceChain(queryProfileId):
	inheritanceChain = []
	currId = queryProfileId
	while True:
		inheritanceChain.append(currId)
		currQpPath = QUERY_PROFILE_PATH + currId + XML_SUFFIX
		try:
			currQp = ET.parse(currQpPath).getroot()
		except IOError:
			print "Could not find file:", currQpPath
			return inheritanceChain
		if INHERITS not in currQp.attrib:
			break
		else:
			currId = currQp.attrib[INHERITS]
	return inheritanceChain

def getQpIC(endpointParserMap):
	eQpICMap = {}
	for endpoint in endpointParserMap:
		eQpICMap[endpoint] = {}
		for bucketName in endpointParserMap[endpoint][QPS]:
			qp = endpointParserMap[endpoint][QPS][bucketName]
			eQpICMap[endpoint][qp] = getQueryProfileInheritanceChain(qp)
	return eQpICMap
		
'''
@returns: rankprofiles for Inheritance chain
'''
def getRankProfileForIC(inheritanceChain):
	rankProfiles = {}
	for queryProfile in inheritanceChain:
		qpPath = QUERY_PROFILE_PATH + queryProfile + XML_SUFFIX
		qp = ET.parse(qpPath).getroot()
		try:
			for field in qp:
				if (RANKING_PROFILE in field.attrib[NAME] or RANK_PROFILE in field.attrib[NAME]) \
					and field.attrib[NAME] not in rankProfiles:
					rankProfiles[field.attrib[NAME]] = field.text
		except KeyError:
			print "Xml schema is different for:", queryProfile
			return rankProfiles
	return rankProfiles

def getRankProfileMap(inheritanceChainMap):
	rankProfileMap = {}
	for endpoint in inheritanceChainMap:
		rankProfileMap[endpoint] = {}
		for qp in inheritanceChainMap[endpoint]:
			rankProfileMap[endpoint][qp] = getRankProfileForIC(inheritanceChainMap[endpoint][qp])
	return rankProfileMap

def getSdRankProfileMap(rankProfileMap):
	sdRankProfileMap = {}
	return sdRankProfileMap

@prettyJsonPrinter
#@prettySheetPrinter
#@jsonWriter(fileName = RANK_PROFILES_ENDPOINTS_JSON)
#@jsonWriter(fileName = RANK_PROFILES_SD_JSON)
#@jsonWriter(fileName = QUERY_PROFILES_JSON)
def getRankProfilesForEndpoints():
	queryProfileMap[DOCS] = getQueryProfiles(DOC_XML_FILE, XML_DOCS_NODE_BEGINNING, XML_DOCS_NODE_ENDING)
	queryProfileMap[MAGZ] = getQueryProfiles(DOC_XML_FILE, XML_MAGS_NODE_BEGINNING, XML_MAGS_NODE_ENDING)
	queryProfileMap[TODAY] = getQueryProfiles(TODAY_XML_FILE, XML_TODAY_NODE_BEGINNING, XML_TODAY_NODE_ENDING)

	endpoints = [e.strip('\n') for e in getLines(ENDPOINTS_PINT_PATH)]
	endpointParserMap = {endpoint: endpointParser(endpoint) for endpoint in endpoints}
	endpointParserMap = addQps(endpointParserMap)
	inheritanceChainMap = getQpIC(endpointParserMap)
	rankProfileMap = getRankProfileMap(inheritanceChainMap)
	sdRankProfileMap = getSdRankProfileMap(rankProfileMap)
	return inheritanceChainMap
	#return rankProfileMap

def main():
	getRankProfilesForEndpoints()

if __name__ == '__main__':
	main()
