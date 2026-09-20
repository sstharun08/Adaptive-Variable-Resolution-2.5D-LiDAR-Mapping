import os
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# SETTINGS
# ==========================================================

RESULTS_FOLDER = "results"
CSV_FILE = os.path.join(
    RESULTS_FOLDER,
    "benchmark_results.csv"
)

FIGURES_FOLDER = os.path.join(
    RESULTS_FOLDER,
    "figures"
)

os.makedirs(
    FIGURES_FOLDER,
    exist_ok=True
)


# ==========================================================
# LOAD DATA
# ==========================================================

data = pd.read_csv(CSV_FILE)

frames = data["Frame"]

# ==========================================================
# FIGURE 1
# FIXED VS ADAPTIVE CELLS
# ==========================================================

plt.figure(figsize=(10, 6))

plt.plot(
    frames,
    data["Fixed_Cells"],
    marker="o",
    label="Fixed 5 cm"
)

plt.plot(
    frames,
    data["Adaptive_Cells"],
    marker="o",
    label="Adaptive 5/10/20 cm"
)

plt.xlabel("LiDAR Frame")
plt.ylabel("Occupied Cells")

plt.title(
    "Fixed vs Adaptive Spatial Representation"
)

plt.xticks(frames)

plt.grid(True, alpha=0.3)

plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_FOLDER,
        "fixed_vs_adaptive_cells.png"
    ),
    dpi=300
)

plt.close()


# ==========================================================
# FIGURE 2
# REPRESENTATION REDUCTION
# ==========================================================

plt.figure(figsize=(10, 6))

plt.plot(
    frames,
    data["Reduction_Percent"],
    marker="o"
)

plt.axhline(
    data["Reduction_Percent"].mean(),
    linestyle="--",
    label=(
        f"Average = "
        f"{data['Reduction_Percent'].mean():.2f}%"
    )
)

plt.xlabel("LiDAR Frame")
plt.ylabel("Representation Reduction (%)")

plt.title(
    "Adaptive Representation Reduction"
)

plt.xticks(frames)

plt.grid(True, alpha=0.3)

plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_FOLDER,
        "representation_reduction.png"
    ),
    dpi=300
)

plt.close()


# ==========================================================
# FIGURE 3
# RESOLUTION DISTRIBUTION
# ==========================================================

average_fine = data["Fine_Cells"].mean()
average_medium = data["Medium_Cells"].mean()
average_coarse = data["Coarse_Cells"].mean()

labels = [
    "Fine 5 cm",
    "Medium 10 cm",
    "Coarse 20 cm"
]

values = [
    average_fine,
    average_medium,
    average_coarse
]

plt.figure(figsize=(8, 6))

plt.bar(
    labels,
    values
)

plt.xlabel("Resolution Level")
plt.ylabel("Average Occupied Cells")

plt.title(
    "Average Adaptive Resolution Distribution"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_FOLDER,
        "resolution_distribution.png"
    ),
    dpi=300
)

plt.close()


# ==========================================================
# FIGURE 4
# PROCESSING TIME
# ==========================================================

plt.figure(figsize=(10, 6))

plt.plot(
    frames,
    data["Processing_Time_ms"],
    marker="o"
)

plt.axhline(
    data["Processing_Time_ms"].mean(),
    linestyle="--",
    label=(
        f"Average = "
        f"{data['Processing_Time_ms'].mean():.2f} ms"
    )
)

plt.xlabel("LiDAR Frame")
plt.ylabel("Processing Time (ms)")

plt.title(
    "Processing Time per LiDAR Frame"
)

plt.xticks(frames)

plt.grid(True, alpha=0.3)

plt.legend()

plt.tight_layout()

plt.savefig(
    os.path.join(
        FIGURES_FOLDER,
        "processing_time.png"
    ),
    dpi=300
)

plt.close()


# ==========================================================
# PRINT RESULTS
# ==========================================================

print()
print("=" * 60)
print("PLOTS GENERATED SUCCESSFULLY")
print("=" * 60)

print()

print(
    "1. fixed_vs_adaptive_cells.png"
)

print(
    "2. representation_reduction.png"
)

print(
    "3. resolution_distribution.png"
)

print(
    "4. processing_time.png"
)

print()

print(
    f"Average reduction: "
    f"{data['Reduction_Percent'].mean():.2f}%"
)

print(
    f"Average processing time: "
    f"{data['Processing_Time_ms'].mean():.2f} ms"
)

print()

print(
    f"Saved to: {FIGURES_FOLDER}"
)

print("=" * 60)