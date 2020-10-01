#! /usr/bin/env python2
import os
import sys
import requests
import csv
import json
import xmltodict
import xml.etree.ElementTree as ET
import pprint
from shashModule import prettyListPrinter

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
SEARCH_PATH = 'pint_homerun/src/main/application/search/'
QUERY_PROFILE_PATH = MASSMEDIA_PATH + SEARCH_PATH + 'query-profiles/'
DOC_XML_FILE = MASSMEDIA_PATH + SEARCH_PATH + 'stateless-handlers.xml'
TODAY_XML_FILE = MASSMEDIA_PATH + SEARCH_PATH + 'stateless-config.xml'
ENDPOINTS_PINT_PATH = 'files/endpoints/endpoints_pint.csv'
RANK_PROFILES_ENDPOINTS_JSON = 'files/endpoints/rankProfilesPint.json'
RANK_PROFILES_SD_JSON = 'files/endpoints/rankProfilesPintSd.json'
QUERY_PROFILES_JSON = 'files/endpoints/queryProfilesPint.json'
DOC_ENDPOINT_PREFIX = '/score/v9/'
MAG_ENDPOINT_PREFIX = '/score/v1/mags/'
MAG_ENDPOINT_SUFFIX = '/finance/ga'
XML_SUFFIX = '.xml'
UNIFIED = 'unified'
FORWARD_SLASH = '/'
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
DASH_MINI = '--------------------------------------------------'
DASH = '---------------------------------------------------------------------------------------------'

def getQueryProfiles(fileName, beginning, ending):
        queryProfiles = {}
        with open(fileName, 'r') as f:
                fileContent = f.read()
                begIndex = fileContent.find(beginning)
                endIndex = fileContent.find(ending, begIndex)
                return xmltodict.parse(fileContent[begIndex: endIndex + len(ending) + 1])
        return queryProfiles

def getDocsEndpoints():
	marketConfigList = queryProfileMap[DOCS][CONFIG][MARKET_CONFIG_MAP][ITEM]
	endpointMap = {}
	prefix = '/score/v9/'
	eInfoMap = {}
	eInfoMap[MARKET] = {}
	eInfoMap[SITE] = {}
	eInfoMap[BUCKET] = {}
	for marketConfigItem in marketConfigList:
		marketConfigKey = marketConfigItem[KEY]
		if type(marketConfigItem[SITE_CONFIG_MAP][ITEM]) == list:
			for siteConfigItem in marketConfigItem[SITE_CONFIG_MAP][ITEM]:
				siteConfigKey = siteConfigItem[KEY]

				#Adding to eInfoMap
				if siteConfigKey not in eInfoMap:
					eInfoMap[siteConfigKey] = {}
				if marketConfigKey not in eInfoMap[siteConfigKey]:
					eInfoMap[siteConfigKey][marketConfigKey] = []
				
				bucketConfigItems = siteConfigItem[SCREEN_CONFIG_MAP][ITEM][BUCKET_CONFIG_MAP][ITEM]
				if type(bucketConfigItems) == list:
					for bucketConfigItem in bucketConfigItems:
						bucketConfigKey = bucketConfigItem[KEY]
						eInfoMap[siteConfigKey][marketConfigKey].append(bucketConfigKey)
				else:
					bucketConfigKey = bucketConfigItems[KEY]
					eInfoMap[siteConfigKey][marketConfigKey].append(bucketConfigKey)
		else: #in which case it has to be a dict
			siteConfigItem = marketConfigItem[SITE_CONFIG_MAP][ITEM]
			siteConfigKey = siteConfigItem[KEY]
			if siteConfigKey not in eInfoMap:
				eInfoMap[siteConfigKey] = {}
			if marketConfigKey not in eInfoMap[siteConfigKey]:
				eInfoMap[siteConfigKey][marketConfigKey] = []
			for bucketConfigItem in siteConfigItem[SCREEN_CONFIG_MAP][ITEM][BUCKET_CONFIG_MAP][ITEM]:
				bucketConfigKey = bucketConfigItem[KEY]
				eInfoMap[siteConfigKey][marketConfigKey].append(bucketConfigKey)
	return eInfoMap

def getMagsEndpoints():
	marketConfigList = queryProfileMap[MAGZ][CONFIG][MARKET_CONFIG_MAP][ITEM]
	eInfoList = []
	#all screenConfigs are default and all categoryConfigs are finance, all buckets are ga or back
	for marketConfigItem in marketConfigList:
		marketConfigKey = marketConfigItem[KEY]
		eInfoList.append(marketConfigKey)
	return eInfoList

def generateDocsEndpoints(endpointsInfo):
	endpoints = []
	endpointBuilder = []

	for site in endpointsInfo:
		for market in endpointsInfo[site]:
			for bucket in endpointsInfo[site][market]:
				endpointBuilder.append(DOC_ENDPOINT_PREFIX)
				endpointBuilder.append(site)
				endpointBuilder.append(FORWARD_SLASH)
				endpointBuilder.append(market)
				endpointBuilder.append(FORWARD_SLASH)
				endpointBuilder.append(UNIFIED)
				endpointBuilder.append(FORWARD_SLASH)
				endpointBuilder.append(bucket)
				endpoints.append("".join(endpointBuilder))
				endpointBuilder = []
			endpointBuilder = []
		endpointBuilder = []
	return endpoints

def generateMagsEndpoints(endpointsInfoList):
	endpoints = []
	for market in endpointsInfoList:
		endpoints.append(MAG_ENDPOINT_PREFIX + market + MAG_ENDPOINT_SUFFIX)
	return endpoints 

def getRankProfilesForEndpoints():
	queryProfileMap[DOCS] = getQueryProfiles(DOC_XML_FILE, XML_DOCS_NODE_BEGINNING, XML_DOCS_NODE_ENDING)
	queryProfileMap[MAGZ] = getQueryProfiles(DOC_XML_FILE, XML_MAGS_NODE_BEGINNING, XML_MAGS_NODE_ENDING)

	endpointsInfoMap = getDocsEndpoints()
	endpointsDocs = generateDocsEndpoints(endpointsInfoMap)
	endpointsInfoList = getMagsEndpoints()
	endpointsMags = generateMagsEndpoints(endpointsInfoList)
	for e in endpointsDocs:
		print e
	print(DASH)
	for e in endpointsMags:
		print e

def main():
	getRankProfilesForEndpoints()

if __name__ == '__main__':
	main()
