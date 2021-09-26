import csv
import sys

if(__name__ == "__main__"):
    args = sys.argv[1:]

    print('Command Line:')
    print('\tCSV File: {}'.format(args[0]))

    with open(args[0]) as csv_file:
        spam_reader = csv.reader(csv_file, delimiter='|')

        header = next(spam_reader)
        print(len(header))