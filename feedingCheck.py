#!/usr/bin/env python2
import os
import sys
import requests
import csv
import json
import requests
import time
from urlparse import urlparse

HTTPS               = 'https://'
HOSTNAME_DEV_US        = 'stream-ranking--by-shashwath.us-east-1.dev.vespa.oath.cloud'
HOSTNAME_DEV_PINT      = 'stream-ranking-pint--by-shashwath.us-east-1.dev.vespa.oath.cloud'
HOSTNAME_CANARY_US     = 'stream-ranking-canary--stream.us-west-1.vespa.oath.cloud'
HOSTNAME_CANARY_PINT   = 'stream-pint-canary--stream.us-west-1.vespa.oath.cloud'
ENDPOINT_DOC_LOOKUP_PREFIX = '/document/v1/slingstone/'
ENDPOINT_DOC_LOOKUP_SUFFIX = '/docid/'
PORT                = '4443'
RISE_FEATURES       = 'rise_features'
FILTER_TAGS         = 'filter_tags'
SID1                = '?sid=kayNy9x4ZA--'
SID3                = '?sid=5DWNpI6Nkw--'
SID2                = '?sid=48zZfbM73w--'  #finance
SID                 = ''
UPDATE_FILE_PATH    = 'files/docs/update/'
FORWARD_SLASH       = '/'
JSON_EXT            = '.json'
ROLETOKEN	    = 'roletoken'
FIELDS		    = 'fields'
PUBLISH_TIME	    = 'publish_time'
YAHOO_ROLE_AUTH     = 'Yahoo-Role-Auth'
CONTENT_TYPE  	    = 'Content-Type'
CACHE_CONTROL	    = 'Cache-Control'
APPLICATION_JSON    = 'application/json'
NO_CACHE	    = 'no-cache'
POST   		    = 'POST'
SPACE 		    = ' '
COLON		    = ':'
DASH 		    = '--------------------------------------------------------------------------------------'

DEV        = 'dev'
CANARY     = 'canary'
PINT       = 'pint'
US         = 'us'
FIELDS     = u'fields'
UUID       = 'uuid'
ASSIGN	   = 'assign'
fieldsUs   = ['rise_features', 'embargo', 'expire', 'filter_tags']
fieldsPint = ['rise_features', 'embargo', 'expire']
keys       = {}
headers    = {}
folders    = ['ca', 'pint', 'today']

"""
Args:
    param1: hostname 
Returns:
    nothing
Function:
    feeds 5 documents of each doc-type to the hostname specified
    and checks after each feed 
"""
def feedCheck(hostname, market):
	failingLookupUrls = []
	for i in xrange(3):
		for j in xrange(5):
			filePath = UPDATE_FILE_PATH + market + FORWARD_SLASH + folders[i] + FORWARD_SLASH + str(j+1) + JSON_EXT
			lookupUrl = feed(hostname, filePath, folders[i])
			if not check(lookupUrl, hostname):
				failingLookupUrls.append(lookupUrl)
	return failingLookupUrls
	
"""
Args:
    param1: filePath 
Returns:
    lookupUrl to the fed document
Function:
    feeds the document specified in filePath 
"""
def feed(hostname, filePath, folder):
	headers[YAHOO_ROLE_AUTH] = getRoletoken()
	lookupUrl = HTTPS + hostname + COLON + PORT + getEndpointDocLookup(folder)
	lookupUrlWithUuid = ''
	data = {}
	with open(filePath) as f:
		jsonData    = json.load(f)
		jsonToFeed  = updatePublishTime(jsonData)
		lookupUrlWithUuid = lookupUrl + jsonToFeed[FIELDS][UUID][ASSIGN]
		print lookupUrlWithUuid
		print headers
		print json.dumps(jsonToFeed)
		response    = requests.put(lookupUrlWithUuid, data=json.dumps(jsonToFeed), headers=headers)
		print response
		data = response.json()
		print data
	return lookupUrlWithUuid

def prettyPrint(dicto):
	return json.dumps(dicto, sort_keys=True, indent=4)

"""
Args:
    param1: lookupUrl
Returns:
    True if all parameters of documents are okay else false
Function:
    feeds the document specified in filePath 
"""
def check(lookupUrl, hostname):
	print lookupUrl, hostname
	resp = requests.get(lookupUrl)
	respDict = resp.json()
	respDictKeys = []
	if FIELDS in respDict:
		respDictKeys = [str(k) for k in respDict[FIELDS].keys()]
	for key in keys[hostname]:
		if key not in respDictKeys:
			print uuid, key, 'not okay'
			return False
		if key == RISE_FEATURES:
			if not len(respDict[FIELDS][key]) > 1:
				print respDict[FIELDS][UUID], key
		if (hostname == HOSTNAME_DEV_US or hostname == HOSTNAME_CANARY_US) and key == FILTER_TAGS:
			if not len(respDict[FIELDS][key]) > 1:
				print respDict[FIELDS][UUID], key
	return True

"""
Args:
    param1: doc-type folder name
Returns:
    endpoint for doc lookup without uuid
"""
def getEndpointDocLookup(folder):
	return ENDPOINT_DOC_LOOKUP_PREFIX + folder + ENDPOINT_DOC_LOOKUP_SUFFIX

"""
Args:
    param1: vespa payload 
Returns:
    payload with publish_time updated to now 
"""
def updatePublishTime(vespaPayload):
	curr_timestamp  = int(time.time()) * 1000
	vespaPayload[FIELDS][PUBLISH_TIME] = {ASSIGN: curr_timestamp}
	return vespaPayload

"""
Args:
    None 
Returns:
    roletoken for making vespa calls 
"""
def getRoletoken():
	return os.environ.get(ROLETOKEN)

"""
Args:
    param1: env 
Returns:
    feed function which feeds to us and pint markets with printed messages
    before and after feeding 
"""
def feedDecorator(env):
	printedUsFunc   = lambda: None
	printedPintFunc = lambda: None
	if env == DEV:
		printedUsFunc   = printDecorator(HOSTNAME_DEV_US  , US  , DEV)
		printedPintFunc = printDecorator(HOSTNAME_DEV_PINT, PINT, DEV)
	else:
		printedUsFunc   = printDecorator(HOSTNAME_CANARY_US  , US  , CANARY)
		printedPintFunc = printDecorator(HOSTNAME_CANARY_PINT, PINT, CANARY)
		
	def feedFunc():
		printedUsFunc()
		printedPintFunc()
	return feedFunc

"""
Args:
    param1: hostname
    param2: market
    param3: env 
Returns:
    feed function with printed messages before and after feeding
"""
def printDecorator(hostname, market, env):
	def printAsYouFeed():
		print market + SPACE + env
		failingLookupUrls = feedCheck(hostname, market)
		if not len(failingLookupUrls) == 0:
			print hostname + COLON
			print failingLookupUrls
		print DASH
	return printAsYouFeed

"""
Args:
    param1: sysargv - gets env as system input 
Returns:
    Nothing
Function:
    Gets the appropriate feedFunc for the env and then calls it 
"""
def main():
	init()
	feedFunc = lambda: None		#initializing an empty function
	if len(sys.argv) == 1 or sys.argv[1] == DEV:
		feedFunc = feedDecorator(DEV) 
	elif sys.argv[1] == CANARY:
		feedFunc = feedDecorator(CANARY)
	feedFunc()

"""
Args:
    None 
Returns:
    Nothing
Function:
    update dict keys with hostnames as keys 
    update dict headers with basic header keys and values
"""
def init():
	#keys
	keys[HOSTNAME_DEV_US]      = fieldsUs
	keys[HOSTNAME_DEV_PINT]    = fieldsPint
	keys[HOSTNAME_CANARY_US]   = fieldsUs
	keys[HOSTNAME_CANARY_PINT] = fieldsPint
	#headers
	headers[CONTENT_TYPE]      = APPLICATION_JSON
	headers[CACHE_CONTROL]     = NO_CACHE

if __name__ == "__main__":
	main() 
