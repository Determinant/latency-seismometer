import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate configuration files for a run.')
    parser.add_argument('--ips', type=str, default='ips.txt',
                        help='text file with all IPs')
    args = parser.parse_args()

    print("[nodes_setup]")
    host_idx_count = {}
    ips = []
    with open(args.ips, "r") as rfile:
        for line in rfile:
            ips.append(line.strip().split()[0])
    machines = sorted(ips)
    print("\n".join(machines))
    print("\n[nodes]")
    for (i, pub_ip) in enumerate(ips):
        host_idx = host_idx_count.setdefault(pub_ip, 0)
        host_idx_count[pub_ip] += 1
        print("replica{} ansible_host={} host_idx={}".format(
                i, pub_ip, host_idx))
