import csv
import sys
import os
import string
import time

def readCSVFile(dimension, column_data, row_data, file_path):
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')

        header = next(csv_reader)
        columns = len(header)
        read_column = []

        # filter out attributes
        for i in range(columns):
            # record id and type (label)
            if 'id' in header[i] or 'type' in header[i]:
                if 'id' == header[i]:
                    # obtain label from filename
                    column_data.append(os.path.basename(file_path).split('_')[0].lower())
                elif 'type' == header[i]:
                    # type_label
                    column_data.append(header[i] + '_' + os.path.basename(file_path).split('_')[0].lower())
                else:
                    # label.id
                    column_data.append(header[i][0:-3].lower())
                
                read_column.append(i)

        dimension.append(len(column_data))
        rows = 0
        for i in range(len(column_data)): row_data.append([])
        
        for row in csv_reader:
            rows += 1

            crt_column = 0
            column_index = 0
            for item in row:
                if crt_column in read_column:
                    row_data[column_index].append(item)
                    column_index += 1
                crt_column += 1

        dimension.append(rows)

def getFiles(directory, file_type):
    file_names = []
    for root, dirs, files in os.walk(directory):
        for i in files:
            if os.path.splitext(i)[1] == file_type:
                file_names.append(i)
    return file_names

def countLabelType(column_datas, row_datas):
    labels = []
    for column_data in column_datas:
        for column in column_data:
            if 'type' in column:
                file_index = column_datas.index(column_data)
                column_index = column_data.index(column)

                for item in row_datas[file_index][column_index]:
                    if not column.split('_')[-1] + '_' + item in labels:
                        labels.append(column.split('_')[-1] + '_' + item)
            elif not column in labels:
                labels.append(column)

    for label in labels:
        if '_' in label:
            if label.split('_')[0] in labels:
                labels.remove(label.split('_')[0])

    return labels

def countLabelNum(labels, column_datas, row_datas, original_ids, num_vertex_offset):
    id_sets = [set() for i in range(len(labels))]

    i_index = 0
    for column_data in column_datas:
        # this is the file that records vertices without type
        if len(column_data) == 1:
            label_index = labels.index(column_data[0])
            for item in row_datas[i_index][0]:
                id_sets[label_index].add(item)
        # this is the file that records vertices with type
        elif 'type' in column_data[1]:
            j_index = 0
            for item in row_datas[i_index][0]:
                label_type = row_datas[i_index][1][j_index]
                label_index = labels.index(column_data[0] + '_' + label_type)
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

def getVertexId(vertex_label_index, original_ids, v_id, v_label):
    if vertex_label_index != -1:
        return original_ids[vertex_label_index][v_id]
    else:
        label_index = 0
        for label in labels:
            if v_label in label:
                if v_id in original_ids[label_index]:
                    return original_ids[label_index][v_id]
            label_index += 1

def countEdge(column_datas, row_datas, original_ids, labels):
    edge_set = set()
    i_index = 0
    for row_data in row_datas:
        if len(column_datas[i_index]) == 1:
            i_index += 1
            continue
        elif 'type' in column_datas[i_index][1]:
            i_index += 1
            continue
        else:
            v1_label = column_datas[i_index][0]
            v2_label = column_datas[i_index][1]

            v1_label_index = -1
            v2_label_index = -1
            if v1_label in labels:
                v1_label_index = labels.index(v1_label)
            if v2_label in labels:
                v2_label_index = labels.index(v2_label)

            for i in range(len(row_data[0])):
                v1 = row_data[0][i]
                v2 = row_data[1][i]
                
                v1_vertex_id = getVertexId(v1_label_index, original_ids, v1, v1_label)
                v2_vertex_id = getVertexId(v2_label_index, original_ids, v2, v2_label)
                
                # remove self loop
                # if v2_vertex_id != v1_vertex_id:
                edge_set.add((v1_vertex_id, v2_vertex_id))

            i_index += 1

    edge_list = []
    for edge in edge_set:
        edge_list.append(edge)

    return edge_list

def getNeighborList(edge_list, in_neighbor_list, out_neighbor_list, in_degree, out_degree):
    for edge in edge_list:
        out_neighbor_list[edge[0]].append(edge[1])
        in_neighbor_list[edge[1]].append(edge[0])
    for each_list in in_neighbor_list:
        in_degree.append(len(each_list))
    for each_list in out_neighbor_list:
        out_degree.append(len(each_list))

def writeGraph(output_file, num_vertices, num_vertex_offset, in_degree, out_degree, in_neighbor_list, out_neighbor_list):
    with open(output_file, 'wb') as f:
        f.write(num_vertices.to_bytes(4, byteorder='little'))
        f.write(len(num_vertex_offset).to_bytes(4, byteorder='little'))

        for offset in num_vertex_offset:
            f.write(offset.to_bytes(4, byteorder='little'))
        
        for each_in_degree in in_degree:
            f.write(each_in_degree.to_bytes(4, byteorder='little'))
        for each_out_degree in out_degree:
            f.write(each_out_degree.to_bytes(4, byteorder='little'))

        for each_in_neighbor_list in in_neighbor_list:
            for each_in_neighbor in each_in_neighbor_list:
                f.write(each_in_neighbor.to_bytes(4, byteorder='little'))
        for each_out_neighbor_list in out_neighbor_list:
            for each_out_neighbor in each_out_neighbor_list:
                f.write(each_out_neighbor.to_bytes(4, byteorder='little'))

if(__name__ == "__main__"):
    args = sys.argv[1:]

    print('Command Line:')
    print('\tDirectory: {}'.format(args[0]))
    print('--------------------------------')

    start = time.process_time()
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

        dimensions.append(dimension)
        column_datas.append(column_data)
        row_datas.append(row_data)
    end = time.process_time()

    print('Time(Loading files): ' + str(end - start) + 's')
    print('The number of files: {}'.format(len(dimensions)))
    print('--------------------------------')

    print('counting labels...')
    labels = countLabelType(column_datas, row_datas)
    print('|\u03A3|: {}'.format(len(labels)))
    print('--------------------------------')

    print('counting vertices...')
    start = time.process_time()
    original_ids = [{} for i in range(len(labels))]
    num_vertex_offset = [0 for i in range(len(labels) + 1)]
    countLabelNum(labels, column_datas, row_datas, original_ids, num_vertex_offset)
    num_vertices = num_vertex_offset[-1]
    end = time.process_time()
    print('Time(Counting vertices): ' + str(end - start) + 's')
    print('--------------------------------')

    print('counting edges...')
    start = time.process_time()
    edge_list = countEdge(column_datas, row_datas, original_ids, labels)
    num_edges = len(edge_list)
    end = time.process_time()
    print('Time(Counting edges): ' + str(end - start) + 's')
    print('--------------------------------')

    print('|V|: {0}, |E|: {1}'.format(num_vertices, num_edges))
    print('--------------------------------')

    in_neighbor_list = [[] for i in range(num_vertices)]
    out_neighbor_list = [[] for i in range(num_vertices)]
    in_degree = []
    out_degree = []
    getNeighborList(edge_list, in_neighbor_list, out_neighbor_list, in_degree, out_degree)

    start = time.process_time()
    base_path = os.path.basename(args[0])
    output_file = base_path + '.graph'
    print('storing graph (path is ' + output_file + ')...')
    writeGraph(output_file, num_vertices, num_vertex_offset, in_degree, out_degree, in_neighbor_list, out_neighbor_list)
    end = time.process_time()
    print('Time(Storing graph): ' + str(end - start) + 's')
    print('--------------------------------')
