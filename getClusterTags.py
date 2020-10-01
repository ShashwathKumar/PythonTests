#!/usr/bin/env python2
import os
import sys
import requests
import csv
import json
import time
from urlparse import urlparse

CLUSTER_TAG = "clusterTag"
LANG = "lang"
REGION = "region"
NO_CLUSTERING = "no_clustering"
CLUSTER_TAG_FILE = "files/cluster/prod.json"
FOUR_PAD = "    "
INVERTED_COMMA = '"'
EN_US = "en-US"
CARD = "card"

"""
Class to collect required values from clusterTag json
"""
class ClusterTagObj(object):
	def __init__(self, clusterTagMap):
		self.clusterTag = clusterTagMap[CLUSTER_TAG]
		self.lang = clusterTagMap[LANG]
		self.region = clusterTagMap[REGION]
		self.site = "homerun"

	def __str__(self):
		return ','.join((self.lang, self.region, self.site))

	def getClusterTag(self):
		return self.clusterTag


"""
Args:
    param1: clusterTagObj
Returns:
    returns a string when printed resembles an xml tag for query profile 
"""
def jsonToClusterTagObjList(clusterTagFile):
	mapList = []
	with open(clusterTagFile, 'r') as f:
		mapList = json.load(f)
	#return list(map(lambda m: ClusterTagObj(m), filter(lambda m: m[CLUSTER_TAG] != NO_CLUSTERING and m[LANG] != EN_US and CARD not in m[CLUSTER_TAG], mapList)))
	return list(map(lambda m: ClusterTagObj(m), filter(lambda m: m[CLUSTER_TAG] != NO_CLUSTERING and CARD not in m[CLUSTER_TAG], mapList)))
	
"""
Args:
    param1: clusterTagObj
Returns:
    returns a string when printed resembles an xml tag for query profile 
"""
def printXmlTag(clusterTagObj):
	PREFIX_QUERY_PROFILE = "<query-profile for="
	PREFIX_FIELD = "<field name="
	NAME_FIELD = '"feed.main.clusterTag"'
	SUFFIX_QUERY_PROFILE = "</query-profile>"
	SUFFIX_FIELD = "</field>"
	SUFFIX_XML = ">"

	line1 = PREFIX_QUERY_PROFILE + INVERTED_COMMA + str(clusterTagObj) + INVERTED_COMMA + SUFFIX_XML
	line2 = FOUR_PAD + PREFIX_FIELD + NAME_FIELD + SUFFIX_XML + clusterTagObj.getClusterTag() + SUFFIX_FIELD
	line3 = SUFFIX_QUERY_PROFILE
	print '\n'.join((line1, line2, line3))

"""
Args:
    param1: sysargv - gets env as system input 
Returns:
    Nothing
Function:
    Gets the appropriate feedFunc for the env and then calls it 
"""
def main():
	clusterTagObjList = jsonToClusterTagObjList(CLUSTER_TAG_FILE)
	map(lambda obj: printXmlTag(obj), clusterTagObjList) 

if __name__ == "__main__":
	main()
