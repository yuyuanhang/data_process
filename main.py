import csv
import sys

if(__name__ == "__main__"):
    args = sys.argv[1:]

    print('Command Line:')
    print('\tCSV File: {}'.format(args[0]))

    with open(args[0]) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')

        header = next(csv_reader)
        columns = len(header)

        columnTypes = {}
        for i in range(columns): columnTypes[i] = None

        rows = 0
        row_data = [[] for i in range(columns)]
        for row in csv_reader:
            rows += 1

            if len(row) != columns:
                continue

            crt_column = 0
            for item in row:
                row_data[crt_column].append(item)
                crt_column++

        print('Column: {}'.format(columns))
        print('Row: {}'.format(rows))

        for i in range(10):
            for j in range(columns):
                print(row_data[j][i])