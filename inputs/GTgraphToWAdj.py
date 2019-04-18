'''
Converts weighted graphs in GTgraph format to the WeightedAdjacencyGraph format of Ligra.
Can optionally set a flag to include back edges for use by a maximum flow algorithm.

Note that GTgraph creates multigraphs; this script handles duplicate edges; the latest (in-file)
update to an edge's weight will be the one used in the final result.

Also includes symmetric back edges as a convenience for LIGRA.
'''

import sys

def int_tuple(list):
    return tuple([int(item) for item in list])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Input format: python GTgraphToWAdj.py <input_file> <output_file>")
        sys.exit(0)
    lines = []
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    V, E = int_tuple(lines[7].strip().split(" ")[2:])
    lines, adj_list = lines[8:], [{} for i in range(V)]
    for line in lines:
        u, v, w = int_tuple(line.strip().split(" ")[1:])
        adj_list[u - 1][v - 1] = w
    # Get node / edge counts with duplicates handled
    V_a, E_a = len(adj_list), 0
    for u in adj_list:
        E_a += len(u)
    # Insert back edges
    back_edges_added = 0
    for i in range(len(adj_list)):
        u = adj_list[i]
        for v in u:
            if u[v] != 0:
                if i not in adj_list[v]:
                    back_edges_added += 1
                adj_list[v][i] = 0
    print("Processed graph has " + str(V_a) + " nodes and " + str(E_a) + " edges")
    print("Processing the graph added " + str(back_edges_added) + " back edges")
    out_lines = ["WeightedAdjacencyGraph\n", str(V_a) + "\n", str(E_a + back_edges_added) + "\n"]
    edges, weights, offset = [], [], 0
    for u in adj_list:
        out_lines.append(str(offset) + "\n")
        for v in u:
            w = u[v]
            edges.append(str(v) + "\n")
            weights.append(str(w) + "\n")
        offset += len(u)
    with open(sys.argv[2], 'w') as out:
        out.writelines(out_lines)
        out.writelines(edges)
        out.writelines(weights)

    