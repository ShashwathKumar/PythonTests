#! /usr/bin/env python3
import os
import sys
import requests
import csv
import json
import xmltodict
import xml.etree.ElementTree as ET
from shashModule import filterEmptyValsMapDecorator 
from shashModule import prettyMapPrinter
from shashModule import prettyJsonPrinter
from shashModule import prettySheetPrinter
from shashModule import jsonWriter
from shashModule import getFilesInDir
from shashModule import prettyJsonPrint

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
QUERY_PROFILE_PATH = MASSMEDIA_PATH + 'homerun/src/main/application/search/query-profiles/jarvis/'
ENDPOINT_XML_FILE = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/homerun/src/main/application/search/stateless-config.xml'
ENDPOINTS_US_PATH = 'files/endpoints/epsCode.csv'
RANK_PROFILES_JSON = 'files/endpoints/rpsCode.json'
XML_SUFFIX = '.xml'
XML_NODE_BEGINNING = '<queryProfileMap>' 
XML_NODE_ENDING    = '</queryProfileMap>'
RANKING_PROFILE = 'ranking.profile'
RANK_PROFILE = 'rankProfile'
QUERY_PROFILE = 'query-profile'
INHERITS = 'inherits'
KEY = 'key'
NAME = 'name'
NAME_KEY = '@name'
TEXT = '#text'
FOR_KEY = '@for'
FIELD = 'field'
DASH = '---------------------------------------------------------------------------------------------'

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


def getQpDict(fileName):
        queryProfiles = {}
        with open(fileName, 'r') as f:
                fileContent = f.read()
                return xmltodict.parse(fileContent)
        return queryProfiles

def getRPFromQpFields(fields):
	rps = {}
	if type(fields) == list:
		for field in fields:
			if RANKING_PROFILE in field[NAME_KEY]:
				rps[field[NAME_KEY]] = field[TEXT]
	else: #in which case it is a dict
		if RANKING_PROFILE in fields[NAME_KEY]:
			rps[fields[NAME_KEY]] = fields[TEXT]
	return rps

def getRankProfiles(qp):
	rps = {}
	
	if FIELD in qp[QUERY_PROFILE]:
		rps = getRPFromQpFields(qp[QUERY_PROFILE][FIELD])

	#going through each internal query-profile
	if QUERY_PROFILE in qp[QUERY_PROFILE]:
		if type(qp[QUERY_PROFILE][QUERY_PROFILE]) == list:
			for qpInternal in qp[QUERY_PROFILE][QUERY_PROFILE]:
				rps[qpInternal[FOR_KEY]] = getRPFromQpFields(qpInternal[FIELD])
		else: #in which case it is a dict
			qpInternal = qp[QUERY_PROFILE][QUERY_PROFILE]
			rps[qpInternal[FOR_KEY]] = getRPFromQpFields(qpInternal[FIELD])
	return rps

def getFlattenedRps(rankProfilesInQs):
	rps = set()
	for stream, rpDict in rankProfilesInQs.items():
		for k, v in rpDict.items():
			if type(v) == dict:
				#print(v)
				rps.update(list(v.values()))
			else:
				rps.add(v)
	return rps

@prettyJsonPrinter
@filterEmptyValsMapDecorator
def getRankProfilesForEndpoints():
	qps = getFilesInDir(QUERY_PROFILE_PATH)
	qpDicts = {qp[:-4]: getQpDict(QUERY_PROFILE_PATH + qp) for qp in qps}
	rankProfilesInQps = {qpName: getRankProfiles(qpDicts[qpName]) for qpName in qpDicts}
	flattenedRps = getFlattenedRps(rankProfilesInQps)
	print("Flattened rank-profiles")
	print(flattenedRps)
	print(DASH)
	return rankProfilesInQps
	
def main():
	getRankProfilesForEndpoints()

if __name__ == '__main__':
	main()
