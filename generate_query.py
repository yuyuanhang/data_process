import sys
import main

def loadLDBCLabels():
	labels = ['person', 'comment', 'forum', 'tag', 'post', 'tagclass', 'country', 'city', 'continent', 'company', 'university']
	return labels

if(__name__ == "__main__"):
	labels = loadLDBCLabels()
	args = sys.argv[1:]

	print('Command Line:')
	print('\tDirectory: {}'.format(args[0]))
	print('--------------------------------')

	with open(args[0]) as query_file:
		line = query_file.readline()
		num_edges = int(line)

		edges = []
		for i in range(num_edges):
			line = query_file.readline()
			edges.append((line.split(' ')[0], line.split(' ')[1][:-1]))

		vertices = set()
		for edge in edges:
			if not edge[0] in vertices:
				vertices.add(edge[0])
			if not edge[1] in vertices:
				vertices.add(edge[1])

		num_vertices = len(vertices)
		num_vertex_offset = [0]

		for label in labels:
			nlf = 0
			for vertex in vertices:
				if label in vertex:
					nlf = nlf + 1
			num_vertex_offset.append(nlf)

		for i in range(len(labels)):
			num_vertex_offset[i + 1] = num_vertex_offset[i] + num_vertex_offset[i + 1]

		edge_list = []
		for edge in edges:
			label1 = edge[0].split('_')[0]
			label2 = edge[1].split('_')[0]
			label1_index = labels.index(label1)
			label2_index = labels.index(label2)
			offset_in_label1 = int(edge[0].split('_')[1]) - 1
			offset_in_label2 = int(edge[1].split('_')[1]) - 1
			edge_list.append((num_vertex_offset[label1_index] + offset_in_label1, num_vertex_offset[label2_index] + offset_in_label2))

	in_neighbor_list = [[] for i in range(num_vertices)]
	out_neighbor_list = [[] for i in range(num_vertices)]
	in_degree = []
	out_degree = []
	main.getNeighborList(edge_list, in_neighbor_list, out_neighbor_list, in_degree, out_degree)
	main.writeGraph(args[1], num_vertices, num_vertex_offset, in_degree, out_degree, in_neighbor_list, out_neighbor_list)