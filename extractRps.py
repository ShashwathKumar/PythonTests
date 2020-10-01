import os
import sys
import requests
from collections import namedtuple
from typing import NamedTuple
from shashModule import getLines
from shashModule import filterEmptyValsMapDecorator
from shashModule import prettyJsonPrinter
from shashModule import jsonWriter
from shashModule import getLinesWithPattern
from shashModule import getJson
from shashModule import prettySheetPrinter

##By default this file works only with ca.sd.template
MASSMEDIA_PATH = '/Users/shashwath/GitYahoo2/MASSMEDIA/massmedia_serving/'
RANK_PROFILE_PATH = MASSMEDIA_PATH + 'homerun/config/searchdefinitions/'
SD_FILE = RANK_PROFILE_PATH + 'ca.sd.template'
RANK_PROFILE = 'rank-profile'
INHERITS = 'inherits'
RPS_ENDLINE = 'document-summary minimal {' #manually found endline after all rps
RANK_PROPERTIES = 'rank-properties'
MACRO = 'macro'
SPACE = ' '
SUMMARY_FEATURES = 'summary-features'
RANK_FEATURES = 'rank-features'
FIRST_PHASE = 'first-phase'
SECOND_PHASE = 'second-phase'
OPEN_BRACE = '{'
CLOSE_BRACE = '}'
OPEN_BRACE_SPACE = ' {'
REFINED_RPS_JSON = 'files/endpoints/refinedRps.json'
RP_PROPS =      [
		RANK_PROPERTIES + OPEN_BRACE_SPACE,
		SUMMARY_FEATURES + OPEN_BRACE_SPACE,
		RANK_FEATURES + OPEN_BRACE_SPACE
		]
RP_PROPS_EXPS = [
		FIRST_PHASE + OPEN_BRACE_SPACE,
		SECOND_PHASE + OPEN_BRACE_SPACE
		]
DASH_MINI = '--------------------------------------------------'
DASH = '---------------------------------------------------------------------------------------------'

def getRpParentTuple(line):
	words = line.split()
	return words[1], words[3]

def findIndex(rpStartLines, lineToFind):
	for i, line in enumerate(rpStartLines):
		if lineToFind in line:
			return i

def cleanRp(rp):
	return list(filter(lambda l: len(l)>0 and l[0] != '#', rp))

def getRawRankProfiles():
	rpLines = getLines(SD_FILE)
	rpStartLines = getLinesWithPattern(SD_FILE, RANK_PROFILE, INHERITS)
	rps = {}
	rpsEndLineIndex = findIndex(rpStartLines, RPS_ENDLINE)
	startLineIndex = 0
	patternLineIndex = 0
	for i, rpLine in enumerate(rpLines):
		if patternLineIndex < len(rpStartLines) and \
				 rpLine == rpStartLines[patternLineIndex]:
			patternLineIndex += 1
			endLineIndex = i
			if startLineIndex == 0:
				startLineIndex = i
				continue
			rpName = getRpParentTuple(rpLines[startLineIndex])[0]
			rps[rpName] = list(map(lambda x: x.strip(), rpLines[startLineIndex: endLineIndex]))
			#cleanup rp
			rps[rpName] = cleanRp(rps[rpName])
			startLineIndex = endLineIndex
		elif patternLineIndex == len(rpStartLines) and \
				RANK_PROFILE in rpLine:
			rpName = getRpParentTuple(rpLine)[0]
			rps[rpName] = list(map(lambda x: x.strip(), rpLines[startLineIndex: rpsEndLineIndex]))
			#cleanup rp
			rps[rpName] = cleanRp(rps[rpName])
	return rps

def extractSummaryProp(rp, prop):
	propIndex = None
	for i, line in enumerate(rp):
		if prop in line:
			propIndex = i
			break

	propEndIndex = 0
	propVal = []
	#search through end of a property only if you found the beginning
	if propIndex != None: 
		for i, line in enumerate(rp[propIndex:]):
			if CLOSE_BRACE in line and OPEN_BRACE not in line:
				propEndIndex = i + propIndex
				break
	
		for line in rp[propIndex+1: propEndIndex]:
			propVal.append(line.strip())
	return propVal

def extractExpProp(rp, prop):
	propIndex = None
	for i, line in enumerate(rp):
		if prop in line:
			propIndex = i
			break

	propEndIndex = 0
	propVal = []
	
	if propIndex != None:
		braceStack = []
		for i, line in enumerate(rp[propIndex:]):
			if OPEN_BRACE in line and CLOSE_BRACE not in line:
				braceStack.append(OPEN_BRACE)
			if CLOSE_BRACE in line and OPEN_BRACE not in line:
				braceStack.pop()
			if len(braceStack)==0:
				propEndIndex = i + propIndex
				break

		for line in rp[propIndex + 1: propEndIndex]:
			propVal.append(line.strip())
	return propVal

def getMacroNames(rp):
	macroNames = []
	for line in rp:
		if MACRO in line:
			macroNames.append(line)
	return macroNames

#not very efficient
def getMacros(rp, macroNames):
	macros = {}
	for macroName in macroNames:
		propIndex = None
		for i, line in enumerate(rp):
			if macroName in line:
				propIndex = i
				break
		
		propEndIndex = 0
		propVal = []

		if propIndex != None:
			braceStack = []
			for i, line in enumerate(rp[propIndex:]):
				if OPEN_BRACE in line and CLOSE_BRACE not in line:
					braceStack.append(OPEN_BRACE)
				if CLOSE_BRACE in line and OPEN_BRACE not in line:
					braceStack.pop()
				if len(braceStack)==0:
					propEndIndex = i + propIndex
					break
	
			for line in rp[propIndex+1: propEndIndex]:
				propVal.append(line.strip())

		macros[getMacroName(macroName)] = propVal
	return macros

def getMacroName(macroName):
	return macroName.split(' ')[1]

def propName(prop):
	return prop.split(' ')[0]

def extractValues(rpName, rp) -> dict:
	refinedRp = {}
	for prop in RP_PROPS:
		refinedRp[propName(prop)] = extractSummaryProp(rp, prop)

	for prop in RP_PROPS_EXPS:
		refinedRp[propName(prop)] = extractExpProp(rp, prop)

	#extract macros
	macroNames = getMacroNames(rp)
	refinedRp[MACRO] = getMacros(rp, macroNames)
	return refinedRp

@jsonWriter(fileName = REFINED_RPS_JSON)
@prettyJsonPrinter
@filterEmptyValsMapDecorator
def getRankProfiles() -> dict:
	rawRps: dict = getRawRankProfiles()
	refinedRps: dict = {k: extractValues(k, rawRps[k]) for k in rawRps}	#dict<Rp>
	return refinedRps

def main():
	refinedRps: dict = getRankProfiles()

if __name__ == "__main__":
	main()
