import networkx as nx
import sys
import time
from networkx.algorithms.flow import edmonds_karp
from collections import deque

def int_tuple(list):
    return tuple([int(item) for item in list])

if __name__ == "__main__":
    filename, lines = sys.argv[1], []
    with open(filename) as file:
        lines = file.readlines()
    V, E = int_tuple(lines[7].strip().split(" ")[2:])
    lines, adj_list = lines[8:], [{} for i in range(V)]
    for line in lines:
        u, v, w = int_tuple(line.strip().split(" ")[1:])
        adj_list[u - 1][v - 1] = w
    max_source, max_size, last_item = 0, 0, None
    queue, visited = deque(), set()
    for source in range(len(adj_list)):
        if source not in visited:
            nodes_visited = set()
            queue.append(source)
            nodes_visited.add(source)
            visited.add(source)
            while (queue):
                node = queue.popleft()
                last_item = node
                if node in range(len(adj_list)):
                    for dest in adj_list[node]:
                        weight = adj_list[node][dest]
                        if dest not in visited:
                            queue.append(dest)
                            nodes_visited.add(dest)
                            visited.add(dest)
        if len(nodes_visited) > max_size:
            max_source, max_size = source, len(nodes_visited)
    edge_list = []
    for i in range(len(adj_list)):
        for dest in adj_list[i]:
            w = adj_list[i][dest]
            edge_list.append((i, dest, w))
    print(len(adj_list))
    print(len(edge_list))
    G = nx.DiGraph()
    for edge in edge_list:
        u, v, w = edge
        G.add_edge(u, v, capacity=w)
    #G.add_node(1048573)
    start = time.time()
    R = edmonds_karp(G, max_source, last_item)
    end = time.time()
    print("Max source and farthest destination are " + str(max_source) + " and " + str(last_item))
    print("Maximum flow value is " + str(R.graph['flow_value']))
    print(" Time taken: " + str(1000 * (end - start)) + "ms")
