#! /usr/bin/env python3
import os
import sys
import json
from shashModule import getLines


def test():
	qpList = getLines('files/endpoints/epsCode.csv')
	for qp in qpList:
		ep = qp.split('">')
		print(ep[0])

def main():
	test()

if __name__=="__main__":
	main()
