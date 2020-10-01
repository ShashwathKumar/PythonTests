#!/usr/bin/env python2
import os
import sys
import requests
import csv
import json
import time
from urlparse import urlparse

HTTPS = 'https://'
PORT  = '4443'
ENDPOINT_SUFFIX = '/search/?format=json&yql=select+uuid+from+ca+where+range(publish_time,{}L,{}L)+limit+400%3B'
ENDPOINT_CA_DOC_LOOKUP = '/document/v1/slingstone/ca/docid/'
ENDPOINT_OFFNET_DOC_LOOKUP = '/document/v1/slingstone/offnet/docid/'

HOSTNAMES_US_FILE = 'files/hostnames/hostnamesUSStream.csv'
HOSTNAMES_PINT_FILE = 'files/hostnames/hostnamesPintStream.csv'

ALL    = 'all'
FIRST  = 'first'
PINT   = 'pint'
US     = 'us'
FIELDS = 'fields'
UUID   = 'uuid'
RISE_FEATURES = 'rise_features'
FILTER_TAGS   = 'filter_tags'
keys   = {'us': ['rise_features', 'embargo', 'expire', 'filter_tags'], 'pint': ['rise_features', 'embargo', 'expire']}

def checkEndpoints(market, hostname):
	curr_timestamp  = int(time.time()) * 1000
	start_timestamp = curr_timestamp - 900 * 1000
	complete_endpoint = HTTPS + hostname + ":" + PORT + ENDPOINT_SUFFIX.format(start_timestamp, curr_timestamp)
	resp = requests.get(complete_endpoint)
	elements = []
	elements_cnt = -1
	try:
		respDict = resp.json()
		elementDicts = respDict["root"]["children"]
		elements = [dicto[FIELDS][UUID] for dicto in elementDicts]
		elements_cnt = len(respDict["root"]["children"])
	except:
		print "ker Error"
	print complete_endpoint, "number_of_elements:", elements_cnt
	print "docs good? ", checkDocsForFields(elements, hostname, market)

def checkDocsForFields(elements, hostname, market):
	for uuid in elements:
		endpoint_doc_lookup = HTTPS + hostname + ":" + PORT + ENDPOINT_CA_DOC_LOOKUP + uuid
		#print endpoint_doc_lookup
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
			if key not in respDictKeys:
				print respDict[FIELDS][UUID], key, 'not okay'
				return False
			if key == RISE_FEATURES:
				if not len(respDict[FIELDS][key]) > 1:
					print respDict[FIELDS][UUID], key 
			if market == US and key == FILTER_TAGS:
				if not len(respDict[FIELDS][key]) > 1:
					print respDict[FIELDS][UUID], key
	return True

def checkColos(colos):
	print "US PROD"
	with open(HOSTNAMES_US_FILE) as f:
		hostnames = [x.strip() for x in f.readlines()]
		for hostname in hostnames:
			checkEndpoints(US, hostname)
			print ""
			if colos == FIRST:
				break
	
	print "-----------------------------------------------------------------------------------------------------"
	print "PINT PROD"
	with open(HOSTNAMES_PINT_FILE) as f:
		hostnames = [x.strip() for x in f.readlines()]
		for hostname in hostnames:
			checkEndpoints(PINT, hostname)
			print ""
			if colos == FIRST:
				break

def main():
	if len(sys.argv) == 1 or sys.argv[1] == ALL:
		checkColos(ALL)
	else:
		checkColos(FIRST)

if __name__ == "__main__":
	main() 
