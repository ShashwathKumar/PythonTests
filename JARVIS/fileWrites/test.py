import os
import sys
import csv


def fileAccess():
	with open('test.txt') as f:
		for line in f:
			print(line.strip())

	print('-------------------------------------------------------------------')

	with open('test2.csv') as cf:
		reader = csv.reader(cf, delimiter=' ')
		with open('test3.csv', 'w') as cf2:
			writer = csv.writer(cf2, delimiter=' ')
			for row in reader:
				writer.writerow([row[1]])
	
	
def main():
        fileAccess()

if __name__ == '__main__':
        main()	
