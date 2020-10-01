#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
#shashModule imports
from shashModule import printTuple
from shashModule import printArgs

#hostnames and endpoints
JARVIS_DEV_HOSTNAME = 'https://jarvis--stream-ranking--by-shashwath.us-east-1.dev.vespa.oath.cloud:4443'
JARVIS_NTK_US_ENDPOINT = '/jarvis/v1/getStreams?queryProfile=ntk_single_feed&site=frontpage&region=US&lang=en-US'
JARVIS_PROD_HOSTNAME = 'https://streams.jarvis.yahoo.com'
JARVIS_PROD_NTK_US_ENDPOINT = ''
STREAM_HOSTNAME = 'https://stream-ranking--by-shashwath.us-east-1.dev.vespa.oath.cloud:4443'
STREAM_DOCID_ENDPOINT = '/document/v1/slingstone/today/docid/'

#String constants
TODAY = 'today-'
CA_VIDEO = 'cavideo'
FIELDS = 'fields'
CONTENT_TYPE = 'content_type'
AMPERSAND = '&'
PROD = 'prod'

#json keys
RESULT = 'result'
NTK = 'ntk'
HITS = 'hits'
ID = 'id'
DASH = '--------------------------------------------------------------------------------------------------'

def getHostname(env):
	return JARVIS_PROD_HOSTNAME if env==PROD else JARVIS_DEV_HOSTNAME

def getTodayVideos(uuids):
	print("uuids at getTodayVideos: ", uuids)
	uuidContentTypeTupleList = [requests.get(STREAM_HOSTNAME + STREAM_DOCID_ENDPOINT + TODAY + uuid).json()[FIELDS][CONTENT_TYPE] for uuid in uuids]
	return list(filter(lambda content_type: content_type==CA_VIDEO, uuidContentTypeTupleList))

def getNtkStream(resp):
	hits = resp[RESULT][NTK][HITS]
	return [hit[ID] for hit in hits]

def compareNtkStreams(param, env):
	ntkUSEndpoint = getHostname(env) + JARVIS_NTK_US_ENDPOINT
	ntkUSEndpointExp = ntkUSEndpoint + AMPERSAND + param
	#make jarvis call
	print(f'Normal call {ntkUSEndpoint}')
	respGa = requests.get(ntkUSEndpoint).json()
	print(f'Param call {ntkUSEndpointExp}')
	respExp = requests.get(ntkUSEndpointExp).json()
	#Fetch NTK uuids
	streamGa = getNtkStream(respGa)
	streamExp = getNtkStream(respExp)
	printArgs(streamGa, streamExp)
	#Get video uuids
	videoUuids = getTodayVideos(set(streamGa)-set(streamExp))
	return videoUuids

def main():
	env: str = sys.argv[1]
	printArgs(compareNtkStreams("filter.contentTypes=story,slideshow", env))

if __name__=='__main__':
	main()
