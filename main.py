import csv
import sys

if(__name__ == "__main__"):
    args = sys.argv[1:]

    print('Command Line:')
    print('\tCSV File: {}'.format(args[0]))

    with open(args[0]) as csv_file:
        spamreader = csv.reader(csv_file, delimiter='|')
        print(len(spamreader))