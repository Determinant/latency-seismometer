import os
import re
import pickle
import argparse

node_pat = re.compile(r'node[0-9]+ ansible_host=([^ ]+) host_idx=([0-9]+)')
lat_pat = re.compile(r'([0-9-:TZ]+) INFO ([0-9.]+) ([0-9.]*.*s)')

parser = argparse.ArgumentParser(description='Extract the latency matrix from logs.')
parser.add_argument('dir', help='directory of a run (by ./run.sh)')
parser.add_argument('--output', nargs=1, help='directory of a run (by ./run.sh)')

args = parser.parse_args()

if __name__ == "__main__":
    node_map = {}
    n = 0
    with open(os.path.join(args.dir, 'nodes'), "r") as f:
        for line in f:
            m = node_pat.match(line)
            if m:
                node_map[m[1]] = int(m[2])
                n += 1
    nodes = [None] * n
    for node in node_map:
        nodes[node_map[node]] = node
    matrix = []
    for (i, node) in enumerate(nodes):
        row = [[] for i in range(n)]
        with open(os.path.join(args.dir, 'remote', str(i), 'log', 'stderr'), 'r') as f:
            for line in f:
                m = lat_pat.match(line)
                if m:
                    ns = 0.0
                    if m[3][-2:] == 'ns':
                        ns = float(m[3][:-2])
                    elif m[3][-2:] == 'µs':
                        ns = float(m[3][:-2]) * 1e3
                    elif m[3][-2:] == 'ms':
                        ns = float(m[3][:-2]) * 1e6
                    elif m[3][-1:] == 's':
                        ns = float(m[3][:-1]) * 1e9
                    row[node_map[m[2]]].append((m[1], ns))
        for j in range(n):
            row[j].sort()
        matrix.append((node, row))
    with open(args.output if args.output else 'latency.pickle', 'wb') as f:
        pickle.dump(matrix, f)
