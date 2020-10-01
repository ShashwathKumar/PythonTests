#!/usr/bin/env python2
import os
import sys
import requests
import csv
import json
from urlparse import urlparse

HTTPS               = 'https://'
ENDPOINT_PREFIX     = '/score/v9'
HOSTNAME_US         = 'stateless--stream-ranking--by-shashwath.us-east-1.dev.vespa.oath.cloud'
HOSTNAME_PINT       = 'stateless--stream-ranking-pint--by-shashwath.us-east-1.dev.vespa.oath.cloud'
ENDPOINT_CA_DOC_LOOKUP = '/document/v1/slingstone/ca/docid/'
ENDPOINT_OFFNET_DOC_LOOKUP = '/document/v1/slingstone/offnet/docid/'
PORT                = '4443'
RISE_FEATURES       = 'rise_features'
FILTER_TAGS         = 'filter_tags'
SID1                = '?sid=kayNy9x4ZA--'
SID3                = '?sid=5DWNpI6Nkw--'
SID2                = '?sid=48zZfbM73w--'  #finance
SID                 = ''
PINT_MARKETS_FILE   = 'files/markets/pintMarkets.csv'
US_MARKETS_FILE     = 'files/markets/usMarkets.csv'
HOSTNAMES_US_FILE   = 'files/hostnames/hostnamesUS.csv'
HOSTNAMES_PINT_FILE = 'files/hostnames/hostnamesPint.csv'

ALL    = 'all'
PINT   = 'pint'
US     = 'us'
PROD   = 'prod'
DEV    = 'dev'
ID     = 'id'
FIELDS = u'fields'
UUID   = 'uuid'
keys   = {'us': ['rise_features', 'embargo', 'expire', 'filter_tags'], 'pint': ['rise_features', 'embargo', 'expire']}

def checkEndpoints(market, hostname):
	file     = PINT_MARKETS_FILE if market == 'pint' else US_MARKETS_FILE

	with open(file) as file:
		endpoints_suffixes = [x.strip() for x in file.readlines()]
		for suffix in endpoints_suffixes:
			complete_endpoint = HTTPS + hostname + ":" + PORT + ENDPOINT_PREFIX + suffix + SID
			resp = requests.get(complete_endpoint)
			elements_cnt = -1
			try:
				respDict     = resp.json()
				elementDicts = respDict["yahoo-coke:stream"]["elements"]
				#print json.dumps(elementDicts, sort_keys=True, indent=4)
				elements     = [dicto[ID] for dicto in elementDicts]
				elements_cnt = len(elements)
				inferred_cnt = len(filter(lambda element: element["explain"]["reason"]==u'INFERRED', elementDicts))
			except:
				print "key Error: " + suffix
			print complete_endpoint, "number_of_elements:", elements_cnt, "inferred_cnt:", inferred_cnt
        		print "docs good? ", checkDocsForFields(elements, hostname, market)

def checkDocsForFields(elements, hostname, market):
        for uuid in elements:
                endpoint_doc_lookup = HTTPS + getStreamEndpoint(hostname) + ":" + PORT + ENDPOINT_CA_DOC_LOOKUP + uuid
                resp = requests.get(endpoint_doc_lookup)
                respDict = resp.json()
		respDictKeys = []
		if FIELDS in respDict:
			respDictKeys = [str(k) for k in respDict[FIELDS].keys()]
		else:
			endpoint_doc_lookup = HTTPS + getStreamEndpoint(hostname) + ":" + PORT + ENDPOINT_OFFNET_DOC_LOOKUP + uuid
			resp = requests.get(endpoint_doc_lookup)
			respDict = resp.json()
			respDictKeys = [str(k) for k in respDict[FIELDS].keys()]
                for key in keys[market]:
                        respDictKeys = [str(k) for k in respDict[FIELDS].keys()]
                        if key not in respDictKeys:
                                print uuid, key, 'not okay'
                                return False
                        if key == RISE_FEATURES:
                                if not len(respDict[FIELDS][key]) > 1:
                                        print respDict[FIELDS][UUID], key
                        if market == US and key == FILTER_TAGS:
                                if not len(respDict[FIELDS][key]) > 1:
                                        print respDict[FIELDS][UUID], key
        return True

def getStreamEndpoint(hostname):
	return hostname[11:]

def checkEndpointsProd():
	hostnamesUSFile   = HOSTNAMES_US_FILE
	hostnamesPintFile = HOSTNAMES_PINT_FILE
	print "US PROD"
	with open(hostnamesUSFile) as f:
		hostnames = [x.strip() for x in f.readlines()]
		for hostname in hostnames:
			checkEndpoints(US, hostname)
			print ""
	
	print "-----------------------------------------------------------------------------------------------------"
	print "PINT PROD"
	with open(hostnamesPintFile) as f:
		hostnames = [x.strip() for x in f.readlines()]
		for hostname in hostnames:
			checkEndpoints(PINT, hostname)
			print ""

def checkEndpointsDev():
	print "US DEV"
	checkEndpoints(US, HOSTNAME_US)
	print ""
	print "-----------------------------------------------------------------------------------------------------"
	print "PINT PROD"
	checkEndpoints(PINT, HOSTNAME_PINT)
	
def main():
	if len(sys.argv) == 1:
		checkEndpointsProd()
	elif sys.argv[1] == DEV:
		checkEndpointsDev()
	elif sys.argv[1] == PINT:
		checkEndpoints(PINT, HOSTNAME_PINT)
	elif sys.argv[1] == US:
		checkEndpoints(US, HOSTNAME_US)
	elif sys.argv[1] == PROD:
		checkEndpointsProd()

if __name__ == "__main__":
	main() 
