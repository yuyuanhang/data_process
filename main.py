import csv
import sys
import os
import string

def readCSVFile(dimension, column_data, row_data, file_path):
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')

        header = next(csv_reader)
        columns = len(header)
        dimension.append(columns)

        for i in range(columns): column_data.append(header[i])

        rows = 0
        for i in range(columns): row_data.append([])
        
        for row in csv_reader:
            rows += 1

            if len(row) != columns:
                continue

            crt_column = 0
            for item in row:
                row_data[crt_column].append(item)
                crt_column += 1

        dimension.append(rows)

def getFiles(directory, file_type):
    file_names = []
    for root, dirs, files in os.walk(directory):
        for i in files:
            if os.path.splitext(i)[1] == file_type:
                file_names.append(i)
    return file_names

def countLabelType(column_datas):
    labels = []
    for column_data in column_datas:
        for column in column_data:
            if not column in labels:
                labels.append(column)
    return labels

def countLabelNum(labels, column_datas, row_datas, original_ids, num_vertex_offset):
    id_sets = [set() for i in range(len(labels))]

    i_index = 0
    for row_data in row_datas:
        j_index = 0
        for row in row_data:
            label_index = labels.index(column_datas[i_index][j_index])
            for item in row:
                id_sets[label_index].add(item)
            j_index += 1
        i_index += 1

    for i in range(len(labels)):
        num_vertex_offset[i + 1] = num_vertex_offset[i] + len(id_sets[i])
        i_index = 0
        for item in id_sets[i]:
            key = item
            original_ids[i][key] = num_vertex_offset[i] + i_index
            i_index += 1

def countEdge(column_datas, row_datas, original_ids, num_vertex_offset, labels):
    edge_set = set()
    i_index = 0
    for row_data in row_datas:
        v1_type = column_datas[i_index][0]
        v2_type = column_datas[i_index][1]

        v1_label_index = labels.index(v1_type)
        v2_label_index = labels.index(v2_type)

        for i in range(len(row_data[0])):
            v1 = row_data[0][i]
            v2 = row_data[1][i]

            v1_vertex_id = original_ids[v1_label_index][v1]
            v2_vertex_id = original_ids[v2_label_index][v2]

            edge_set.add((v1_vertex_id, v2_vertex_id))

        i_index += 1

    edge_list = []
    for edge in edge_set:
        edge_list.append(edge)

    return edge_list

def countDegree(edge_list, num_vertices):
    vertex_degree = [0 for i in range(num_vertices)]
    for edge in edge_list:
        vertex_degree[edge[0]] += 1
        vertex_degree[edge[1]] += 1
    return vertex_degree

def writeGraph(output_file, num_vertices, num_edges, num_vertex_offset, vertex_degree, edge_list):
    with open(output_file, 'w') as f:
        f.write('t '+str(num_vertices)+' '+str(num_edges)+'\n')

        label_type = 0
        for i in range(num_vertices):
            if i >= num_vertex_offset[label_type + 1]:
                label_type += 1
            f.write('v '+str(i)+' '+str(label_type)+' '+str(vertex_degree[i])+'\n')

        for edge in edge_list:
            f.write('e '+str(edge[0])+' '+str(edge[1])+'\n')

if(__name__ == "__main__"):
    args = sys.argv[1:]

    print('Command Line:')
    print('\tDirectory: {}'.format(args[0]))
    print('--------------------------------')

    files = getFiles(args[0], '.csv')

    dimensions = []
    column_datas = []
    row_datas = []
    for i in range(len(files)):
        print('Reading {}th csv file...'.format(i))
        file_path = os.path.join(args[0], files[i])

        dimension = []
        column_data = []
        row_data = []
        readCSVFile(dimension, column_data, row_data, file_path)

        crt_index = 0;
        while crt_index < len(column_data):
            if not 'id' in column_data[crt_index]:
                del column_data[crt_index]
                del row_data[crt_index]
            else:
                crt_index += 1

        if len(column_data) > 1:
            dimension[0] = len(column_data)
            dimensions.append(dimension)
            column_datas.append(column_data)
            row_datas.append(row_data)
    
    print('The number of files: {}'.format(len(dimensions)))
    print('--------------------------------')
    for i in range(len(column_datas)):
        for j in range(len(column_datas[i])):
            column_datas[i][j] = column_datas[i][j][0:-3]

    labels = countLabelType(column_datas)

    print('counting vertices...')
    original_ids = [{} for i in range(len(labels))]
    num_vertex_offset = [0 for i in range(len(labels) + 1)]
    countLabelNum(labels, column_datas, row_datas, original_ids, num_vertex_offset)
    num_vertices = num_vertex_offset[-1]
    print('--------------------------------')

    print('counting edges...')
    edge_list = countEdge(column_datas, row_datas, original_ids, num_vertex_offset, labels)
    num_edges = len(edge_list)
    print('--------------------------------')

    print('|V|: {0}, |E|: {1}'.format(num_vertices, num_edges))
    print('--------------------------------')

    vertex_degree = countDegree(edge_list, num_vertices)

    print('storing graph...')
    output_file = args[0] + '.graph'
    writeGraph(output_file, num_vertices, num_edges, num_vertex_offset, vertex_degree, edge_list)
    print('--------------------------------')