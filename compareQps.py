import os
import sys
from shashModule import getLines

def main():
	nonFlatLines = getLines("files/nonflat.txt")
	flatLines = getLines("files/flat.txt")

	nonFlatSet = getSetFromList(nonFlatLines)
	flatSet = getSetFromList(flatLines)

	print(nonFlatSet - flatSet)
	print("-----------------------------------------")
	print(flatSet - nonFlatSet)


def getSetFromList(listx):
	setx = set()
	for line in listx:
		openBraceIndex = line.find('(')
		setx.add(line[:openBraceIndex-1])
	return setx


if __name__=="__main__":
	main()
