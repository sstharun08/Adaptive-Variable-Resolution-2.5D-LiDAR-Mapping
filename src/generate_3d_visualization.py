import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------
# Adaptive 2.5D LiDAR Terrain Map — 3D Visualization
# ---------------------------------------------------------

input_file = Path("dataset/000000.bin")

output_dir = Path("demo")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "adaptive_2_5d_terrain_map_3d.png"

# Load KITTI-style LiDAR data: X, Y, Z, intensity
points = np.fromfile(input_file, dtype=np.float32).reshape(-1, 4)

x = points[:, 0]
y = points[:, 1]
z = points[:, 2]

# Distance from vehicle
distance = np.sqrt(x**2 + y**2)

# Useful mapping range
mask = (
    (distance > 2) &
    (distance < 50) &
    (z > -3) &
    (z < 5)
)

x = x[mask]
y = y[mask]
z = z[mask]

# ---------------------------------------------------------
# Adaptive resolution
# ---------------------------------------------------------

resolution = np.where(
    distance[mask] < 10,
    0.05,
    np.where(distance[mask] < 25, 0.10, 0.20)
)

# Common origin
origin_x = np.min(x)
origin_y = np.min(y)

# Assign every point to an adaptive spatial cell
cell_x = np.floor((x - origin_x) / resolution)
cell_y = np.floor((y - origin_y) / resolution)

# ---------------------------------------------------------
# Aggregate points into adaptive cells
# ---------------------------------------------------------

cells = {}

for i in range(len(x)):
    key = (
        int(cell_x[i]),
        int(cell_y[i]),
        float(resolution[i])
    )

    if key not in cells:
        cells[key] = []

    cells[key].append(z[i])

# Calculate cell centre and average elevation
map_x = []
map_y = []
map_z = []
map_resolution = []

for (cx, cy, res), values in cells.items():

    center_x = origin_x + (cx + 0.5) * res
    center_y = origin_y + (cy + 0.5) * res
    center_z = np.mean(values)

    map_x.append(center_x)
    map_y.append(center_y)
    map_z.append(center_z)
    map_resolution.append(res)

map_x = np.array(map_x)
map_y = np.array(map_y)
map_z = np.array(map_z)
map_resolution = np.array(map_resolution)

# ---------------------------------------------------------
# Create 3D visualization
# ---------------------------------------------------------

fig = plt.figure(figsize=(13, 9))

ax = fig.add_subplot(111, projection="3d")

# Resolution categories
fine = map_resolution == 0.05
medium = map_resolution == 0.10
coarse = map_resolution == 0.20

# Plot adaptive cells
ax.scatter(
    map_x[fine],
    map_y[fine],
    map_z[fine],
    c=map_z[fine],
    cmap="viridis",
    s=2.5,
    alpha=0.75,
    label="Fine — 5 cm"
)

ax.scatter(
    map_x[medium],
    map_y[medium],
    map_z[medium],
    c=map_z[medium],
    cmap="viridis",
    s=4,
    alpha=0.75,
    label="Medium — 10 cm"
)

ax.scatter(
    map_x[coarse],
    map_y[coarse],
    map_z[coarse],
    c=map_z[coarse],
    cmap="viridis",
    s=6,
    alpha=0.75,
    label="Coarse — 20 cm"
)

# ---------------------------------------------------------
# Labels and presentation
# ---------------------------------------------------------

ax.set_title(
    "Adaptive 2.5D Terrain Map — 3D Visualization",
    fontsize=18,
    fontweight="bold",
    pad=20
)

ax.set_xlabel("X (m)", fontsize=11)
ax.set_ylabel("Y (m)", fontsize=11)
ax.set_zlabel("Elevation Z (m)", fontsize=11)

ax.view_init(
    elev=32,
    azim=-60
)

ax.set_box_aspect((1, 1, 0.35))

ax.legend(
    loc="upper right",
    fontsize=9
)

# Elevation colour scale
scatter = ax.scatter(
    map_x,
    map_y,
    map_z,
    c=map_z,
    cmap="viridis",
    s=0.01,
    alpha=0
)

colorbar = fig.colorbar(
    scatter,
    ax=ax,
    shrink=0.65,
    pad=0.08
)

colorbar.set_label(
    "Elevation (m)",
    fontsize=11
)

# ---------------------------------------------------------
# Information box
# ---------------------------------------------------------

info = (
    f"Frame: 000000.bin\n"
    f"Adaptive cells: {len(map_x):,}\n"
    f"Fine: {np.sum(fine):,}  |  "
    f"Medium: {np.sum(medium):,}  |  "
    f"Coarse: {np.sum(coarse):,}"
)

fig.text(
    0.02,
    0.02,
    info,
    fontsize=10
)

plt.tight_layout()

plt.savefig(
    output_file,
    dpi=250,
    bbox_inches="tight"
)

plt.close()

print("ADAPTIVE 2.5D VISUALIZATION GENERATED")
print("Saved to:", output_file)
print("Adaptive cells:", len(map_x))
print("Fine cells:", np.sum(fine))
print("Medium cells:", np.sum(medium))
print("Coarse cells:", np.sum(coarse))