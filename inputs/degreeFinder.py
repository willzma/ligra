'''
Returns the two nodes with the highest in-degree and out-degree, respectively,
that are also connected. The highest out-degree should be able to reach the highest in-degree.
'''

from collections import deque
import numpy as np
import sys

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
    in_max, in_argmax, in_degrees = 0, 0, [0] * V
    out_max, out_argmax, out_degrees = 0, 0, [0] * V
    src_considered, sink_considered = set(), set()
    for i, u in enumerate(adj_list):
        out_degrees[i] += len(u)
        for v in u:
            in_degrees[v] += 1
    for i in range(V):
        if in_degrees[i] > in_max:
            in_max = in_degrees[i]
            in_argmax = i
        if out_degrees[i] > out_max:
            out_max = out_degrees[i]
            out_argmax = i
    in_argrees, out_argrees = np.flip(np.argsort(in_degrees)), np.flip(np.argsort(out_degrees))
    for i in in_argrees:
        for j in out_argrees:
            if j == i:
                break
            queue, visited = deque(), set()
            queue.append(out_degrees[j])
            visited.add(out_degrees[j])
            while queue:
                node = queue.popleft()
                for dest in adj_list[node]:
                    if dest not in visited:
                        queue.append(dest)
                        visited.add(dest)
                    if dest == in_argmax:
                        print("Highest in-degree is node " + str(i) + " with in-degree " + str(in_degrees[i]))
                        print("Highest out-degree is node " + str(j) + " with out-degree " + str(out_degrees[j]))
                        sys.exit(0)
        
    