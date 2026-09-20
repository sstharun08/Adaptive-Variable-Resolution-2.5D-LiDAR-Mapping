import os
import csv
import time
import tracemalloc
import numpy as np

# ==========================================================
# SETTINGS
# ==========================================================

DATASET_FOLDER = "dataset"
RESULTS_FOLDER = "results"

FRAMES = range(10)

FINE = 0.05
MEDIUM = 0.10
COARSE = 0.20


# ==========================================================
# CREATE RESULTS FOLDER
# ==========================================================

os.makedirs(
    RESULTS_FOLDER,
    exist_ok=True
)


# ==========================================================
# PROCESS ONE FRAME
# ==========================================================

def process_frame(filepath):

    data = np.fromfile(
        filepath,
        dtype=np.float32
    ).reshape(-1, 4)

    points = data[:, :3]

    x = points[:, 0]
    y = points[:, 1]

    distance = np.sqrt(
        x * x + y * y
    )

    # Adaptive resolution
    resolution = np.where(
        distance < 10.0,
        FINE,
        np.where(
            distance < 25.0,
            MEDIUM,
            COARSE
        )
    )

    origin_x = np.min(x)
    origin_y = np.min(y)

    # ======================================================
    # FIXED 5 CM
    # ======================================================

    fixed_x = np.floor(
        (x - origin_x) / FINE
    ).astype(np.int64)

    fixed_y = np.floor(
        (y - origin_y) / FINE
    ).astype(np.int64)

    fixed_cells = len(
        np.unique(
            np.column_stack(
                (fixed_x, fixed_y)
            ),
            axis=0
        )
    )

    # ======================================================
    # ADAPTIVE
    # ======================================================

    cell_x = np.floor(
        (x - origin_x) / resolution
    ).astype(np.int64)

    cell_y = np.floor(
        (y - origin_y) / resolution
    ).astype(np.int64)

    cell_data = np.column_stack(
        (
            cell_x,
            cell_y,
            resolution
        )
    )

    unique_cells = np.unique(
        cell_data,
        axis=0
    )

    adaptive_cells = len(
        unique_cells
    )

    # Resolution distribution
    fine_cells = np.sum(
        unique_cells[:, 2] == FINE
    )

    medium_cells = np.sum(
        unique_cells[:, 2] == MEDIUM
    )

    coarse_cells = np.sum(
        unique_cells[:, 2] == COARSE
    )

    # Reduction
    reduction = (
        (fixed_cells - adaptive_cells)
        / fixed_cells
        * 100
    )

    return (
        len(points),
        fixed_cells,
        adaptive_cells,
        reduction,
        fine_cells,
        medium_cells,
        coarse_cells
    )


# ==========================================================
# MAIN BENCHMARK
# ==========================================================

print()
print("=" * 75)
print("SIH26053 FINAL LiDAR BENCHMARK")
print("=" * 75)
print()

header = (
    "Frame        Points       Fixed        Adaptive"
    "     Reduction       Fine      Medium      Coarse"
)

print(header)
print("-" * 95)

all_results = []

total_points = 0
total_fixed = 0
total_adaptive = 0

total_fine = 0
total_medium = 0
total_coarse = 0

total_time = 0.0


for frame in FRAMES:

    filename = f"{frame:06d}.bin"

    filepath = os.path.join(
        DATASET_FOLDER,
        filename
    )

    if not os.path.exists(filepath):

        print(
            f"Frame {filename} not found"
        )

        continue

    tracemalloc.start()

    start = time.perf_counter()

    result = process_frame(
        filepath
    )

    end = time.perf_counter()

    current, peak = (
        tracemalloc.get_traced_memory()
    )

    tracemalloc.stop()

    processing_time = (
        end - start
    ) * 1000

    (
        points,
        fixed_cells,
        adaptive_cells,
        reduction,
        fine_cells,
        medium_cells,
        coarse_cells
    ) = result

    peak_memory_mb = (
        peak / (1024 * 1024)
    )

    total_points += points
    total_fixed += fixed_cells
    total_adaptive += adaptive_cells

    total_fine += fine_cells
    total_medium += medium_cells
    total_coarse += coarse_cells

    total_time += processing_time

    all_results.append(
        [
            frame,
            points,
            fixed_cells,
            adaptive_cells,
            reduction,
            fine_cells,
            medium_cells,
            coarse_cells,
            processing_time,
            peak_memory_mb
        ]
    )

    print(
        f"{frame:05d}      "
        f"{points:8,}   "
        f"{fixed_cells:8,}   "
        f"{adaptive_cells:8,}   "
        f"{reduction:8.2f}%   "
        f"{fine_cells:8,}   "
        f"{medium_cells:8,}   "
        f"{coarse_cells:8,}"
    )


# ==========================================================
# FINAL SUMMARY
# ==========================================================

number_of_frames = len(
    all_results
)

if number_of_frames == 0:

    print()
    print("No LiDAR frames were found.")

else:

    average_points = (
        total_points /
        number_of_frames
    )

    average_fixed = (
        total_fixed /
        number_of_frames
    )

    average_adaptive = (
        total_adaptive /
        number_of_frames
    )

    average_reduction = (
        (
            total_fixed -
            total_adaptive
        )
        /
        total_fixed
        *
        100
    )

    average_time = (
        total_time /
        number_of_frames
    )

    average_memory = (
        sum(
            result[9]
            for result in all_results
        )
        /
        number_of_frames
    )

    average_fine = (
        total_fine /
        number_of_frames
    )

    average_medium = (
        total_medium /
        number_of_frames
    )

    average_coarse = (
        total_coarse /
        number_of_frames
    )

    # ======================================================
    # PRINT SUMMARY
    # ======================================================

    print()
    print("=" * 75)
    print("FINAL SUMMARY")
    print("=" * 75)

    print(
        f"Frames tested           : "
        f"{number_of_frames}"
    )

    print(
        f"Total LiDAR points      : "
        f"{total_points:,}"
    )

    print(
        f"Average points/frame    : "
        f"{average_points:,.0f}"
    )

    print(
        f"Average fixed cells     : "
        f"{average_fixed:,.0f}"
    )

    print(
        f"Average adaptive cells  : "
        f"{average_adaptive:,.0f}"
    )

    print(
        f"Average reduction       : "
        f"{average_reduction:.2f}%"
    )

    print(
        f"Average fine cells      : "
        f"{average_fine:,.0f}"
    )

    print(
        f"Average medium cells    : "
        f"{average_medium:,.0f}"
    )

    print(
        f"Average coarse cells    : "
        f"{average_coarse:,.0f}"
    )

    print(
        f"Average processing time : "
        f"{average_time:.2f} ms"
    )

    print(
        f"Average peak memory     : "
        f"{average_memory:.2f} MB"
    )

    # ======================================================
    # SAVE CSV
    # ======================================================

    csv_path = os.path.join(
        RESULTS_FOLDER,
        "benchmark_results.csv"
    )

    with open(
        csv_path,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Frame",
                "Points",
                "Fixed_Cells",
                "Adaptive_Cells",
                "Reduction_Percent",
                "Fine_Cells",
                "Medium_Cells",
                "Coarse_Cells",
                "Processing_Time_ms",
                "Peak_Memory_MB"
            ]
        )

        for row in all_results:

            writer.writerow(row)

    # ======================================================
    # SAVE SUMMARY TXT
    # ======================================================

    summary_path = os.path.join(
        RESULTS_FOLDER,
        "benchmark_summary.txt"
    )

    with open(
        summary_path,
        "w"
    ) as file:

        file.write(
            "SIH26053 FINAL LiDAR BENCHMARK\n"
        )

        file.write(
            "=" * 60 + "\n\n"
        )

        file.write(
            f"Frames tested: {number_of_frames}\n"
        )

        file.write(
            f"Total LiDAR points: "
            f"{total_points:,}\n"
        )

        file.write(
            f"Average points/frame: "
            f"{average_points:,.0f}\n"
        )

        file.write(
            f"Average fixed cells: "
            f"{average_fixed:,.0f}\n"
        )

        file.write(
            f"Average adaptive cells: "
            f"{average_adaptive:,.0f}\n"
        )

        file.write(
            f"Average representation reduction: "
            f"{average_reduction:.2f}%\n"
        )

        file.write(
            f"Average fine cells: "
            f"{average_fine:,.0f}\n"
        )

        file.write(
            f"Average medium cells: "
            f"{average_medium:,.0f}\n"
        )

        file.write(
            f"Average coarse cells: "
            f"{average_coarse:,.0f}\n"
        )

        file.write(
            f"Average processing time: "
            f"{average_time:.2f} ms/frame\n"
        )

        file.write(
            f"Average peak memory: "
            f"{average_memory:.2f} MB\n"
        )

    # ======================================================
    # DONE
    # ======================================================

    print()
    print("=" * 75)
    print("Benchmark complete.")
    print()
    print(
        f"CSV saved to: {csv_path}"
    )
    print(
        f"Summary saved to: {summary_path}"
    )
    print("=" * 75)