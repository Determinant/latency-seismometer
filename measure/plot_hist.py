import pickle
import seaborn as sns
import matplotlib.pyplot as plt

with open("./latency.pickle", "rb") as f:
    matrix = pickle.load(f)

n = len(matrix)

fig, axes = plt.subplots(n, n, figsize=(80, 50))

for i in range(n):
    for j in range(n):
        points = matrix[i][1][j]
        d = {'t': [p[0] / 1e9 for p in points], 'rtt': [p[1] / 1e6 for p in points]}
        sns.histplot(data=d, x='rtt', ax=axes[i][j], bins=100)

fig.tight_layout()
fig.savefig('t.png', dpi=200)
