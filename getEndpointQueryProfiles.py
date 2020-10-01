#! /usr/bin/env python3
import os
import sys
import requests
import csv
import json
import xml.etree.ElementTree as ET
from shashModule import filterEmptyValsMapDecorator 
from shashModule import prettyMapPrinter
from shashModule import prettyJsonPrinter
from shashModule import prettySheetPrinter
from shashModule import jsonWriter

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
QUERY_PROFILE_PATH = MASSMEDIA_PATH + 'homerun/src/main/application/search/query-profiles/'
ENDPOINT_XML_FILE = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/homerun/src/main/application/search/stateless-config.xml'
ENDPOINTS_US_PATH = 'files/endpoints/endpoints_us.csv'
RANK_PROFILES_JSON = 'files/endpoints/rpsCode.json'
XML_SUFFIX = '.xml'
XML_NODE_BEGINNING = '<queryProfileMap>' 
XML_NODE_ENDING    = '</queryProfileMap>'
RANKING_PROFILE = 'ranking.profile'
RANK_PROFILE = 'rankProfile'
INHERITS = 'inherits'
KEY = 'key'
NAME = 'name'

def getEndpointsUs():
	with open(ENDPOINTS_US_PATH, 'r') as f:
		endpointsUs = f.readlines()
		return endpointsUs	

def getCurrQueryProfiles(endpoints):
	queryProfiles = {}
	with open(ENDPOINT_XML_FILE, 'r') as f:
		fileContent = f.read()
		begIndex = fileContent.find(XML_NODE_BEGINNING)
		endIndex = fileContent.find(XML_NODE_ENDING, begIndex)
		root = ET.fromstring(fileContent[begIndex: endIndex + len(XML_NODE_ENDING) + 1])
		for item in root:
			queryProfiles[item.attrib[KEY]] = item.text
	return queryProfiles

'''
@returns: rankprofiles for Inheritance chain
'''
def getRankProfileForIC(inheritanceChain):
	rankProfiles = {}
	for queryProfile in inheritanceChain:
		qpPath = QUERY_PROFILE_PATH + queryProfile + XML_SUFFIX
		qp = ET.parse(qpPath).getroot()
		for field in qp:
			if (RANKING_PROFILE in field.attrib[NAME] or RANK_PROFILE in field.attrib[NAME]) and field.attrib[NAME] not in rankProfiles:
				rankProfiles[field.attrib[NAME]] = field.text
	return rankProfiles

'''
methods credits: aaronnagao
'''
def getQueryProfileInheritanceChain(queryProfileId):
	inheritanceChain = []
	currId = queryProfileId
	while True:
		currQpPath = QUERY_PROFILE_PATH + currId + XML_SUFFIX
		try:
			currQp = ET.parse(currQpPath).getroot()
		except IOError: #in case the queryProfile does not exist
			break
		#Adding the currId to inheritance chain only if it was parsed successfuly
		inheritanceChain.append(currId)
		if INHERITS not in currQp.attrib:
			break
		else:
			currId = currQp.attrib[INHERITS]
	return inheritanceChain

@prettySheetPrinter
@jsonWriter(fileName = RANK_PROFILES_JSON)
@filterEmptyValsMapDecorator
def getRankProfilesForEndpoints():
	endpoints = [e.strip('\n') for e in getEndpointsUs()]
	currQueryProfiles = getCurrQueryProfiles(endpoints)
	inheritanceChainMap = {endpoint: getQueryProfileInheritanceChain(currQueryProfiles[endpoint]) for endpoint in endpoints}
	rankProfileMap = {endpoint: getRankProfileForIC(inheritanceChainMap[endpoint]) for endpoint in endpoints}
	return rankProfileMap

	
def main():
	getRankProfilesForEndpoints()

if __name__ == '__main__':
	main()
