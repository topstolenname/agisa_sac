"""Figure 1 – Persistence Diagram (template)
This script generates a synthetic persistence diagram for illustration.
Replace the synthetic data with real outputs from your TDA pipeline when available.
Requirements: matplotlib (no seaborn). This script intentionally avoids specifying colors.
"""

import random

import matplotlib.pyplot as plt

# Generate synthetic (birth, death) pairs with birth < death
random.seed(42)
n_points = 40
pairs = []
for _ in range(n_points):
    b = random.uniform(0.0, 0.8)
    d = random.uniform(b + 0.02, 1.0)
    pairs.append((b, d))

# Plot
plt.figure(figsize=(5, 5))
plt.scatter([b for b, d in pairs], [d for b, d in pairs], s=18)
# Diagonal reference
plt.plot([0, 1], [0, 1])
plt.xlabel("Birth")
plt.ylabel("Death")
plt.title("Persistence Diagram (Synthetic)")
plt.tight_layout()
plt.savefig("docs/figs/svg/figure1.svg")
# Also save PNG for slide decks
plt.savefig("docs/figs/png/figure1.png", dpi=200)
plt.close()
