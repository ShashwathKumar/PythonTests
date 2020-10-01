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

MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
SD_US_PATH = MASSMEDIA_PATH + 'homerun/config/searchdefinitions'
SD_PINT_PATH = MASSMEDIA_PATH + 'pint_homerun/config/searchdefinitions'
SD_PATHS_US = []
SD_PATHS_PINT = []
DOT = '.'
FORWARD_SLASH = '/'
SD_SUFFIX = '.sd'
FIELD = 'field'
TYPE = 'type'
US = 'us'
PINT = 'pint'
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

	#Going through sd files in SD_US_PATH
	sdFilesUs = getSdPath(next(os.walk(SD_US_PATH)))
	SD_PATHS_US.extend(sdFilesUs)
	
	#Going through sd files in SD_PINT_PATH
	sdFilesPint = getSdPath(next(os.walk(SD_PINT_PATH)))
	SD_PATHS_PINT.extend(sdFilesPint)

def getFields(sdPaths):
	fieldsDict = {}
	for path in sdPaths:
		fieldLines = getLinesWithPattern(path, FIELD, TYPE)
		fields = [fieldLine.strip().split(' ')[1] for fieldLine in fieldLines]
		fieldsDict[getSd(path)] = fields
	return fieldsDict

@prettyJsonPrinter	
#@prettySheetPrinter
@printValidValsMapDecorator
def getSdFields():
	initSdPaths()
	sdFieldsDict = {}
	sdFieldsDict[US] = getFields(SD_PATHS_US)
	sdFieldsDict[PINT] = getFields(SD_PATHS_PINT)
	return sdFieldsDict[PINT]

def main():
	getSdFields()

if __name__ == '__main__':
	main()
