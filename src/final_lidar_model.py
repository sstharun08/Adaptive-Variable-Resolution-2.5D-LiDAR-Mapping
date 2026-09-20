import os
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LiDARApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "SIH26053 - Adaptive Variable Resolution 2.5D LiDAR Mapping"
        )

        self.root.geometry("1500x850")

        # ======================================================
        # DATASET
        # ======================================================

        self.dataset_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dataset"
        )

        self.frame_number = 0

        # ======================================================
        # DATA VARIABLES
        # ======================================================

        self.raw_points = None
        self.adaptive_map = None
        self.ground_map = None
        self.obstacle_map = None

        # ======================================================
        # TITLE
        # ======================================================

        title = tk.Label(
            root,
            text="Adaptive Variable Resolution 2.5D LiDAR Mapping",
            font=("Arial", 20, "bold")
        )

        title.pack(pady=10)

        # ======================================================
        # CONTROL FRAME
        # ======================================================

        control_frame = tk.Frame(root)

        control_frame.pack(pady=5)

        tk.Label(
            control_frame,
            text="Frame:",
            font=("Arial", 11)
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        self.frame_entry = tk.Entry(
            control_frame,
            width=8,
            font=("Arial", 11)
        )

        self.frame_entry.insert(
            0,
            "000000"
        )

        self.frame_entry.pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Load LiDAR
        # ------------------------------------------------------

        tk.Button(
            control_frame,
            text="Load LiDAR",
            command=self.load_lidar,
            width=14
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Adaptive Model
        # ------------------------------------------------------

        tk.Button(
            control_frame,
            text="Run Adaptive Model",
            command=self.run_adaptive_model,
            width=18
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Terrain Analysis
        # ------------------------------------------------------

        tk.Button(
            control_frame,
            text="Terrain Analysis",
            command=self.terrain_analysis,
            width=16
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Final Integrated Map
        # ------------------------------------------------------

        tk.Button(
            control_frame,
            text="Final Integrated Map",
            command=self.final_integrated_map,
            width=20
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Save Results
        # ------------------------------------------------------

        tk.Button(
            control_frame,
            text="Save Results",
            command=self.save_results,
            width=14
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ======================================================
        # STATUS
        # ======================================================

        self.status_label = tk.Label(
            root,
            text="Ready",
            font=("Arial", 11)
        )

        self.status_label.pack(
            pady=5
        )

        # ======================================================
        # MATPLOTLIB FIGURE
        # ======================================================

        self.figure, self.axes = plt.subplots(
            1,
            4,
            figsize=(18, 5)
        )

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=root
        )

        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=10
        )

    # ==========================================================
    # LOAD LIDAR
    # ==========================================================

    def load_lidar(self):

        try:

            frame_text = self.frame_entry.get().strip()

            frame_number = int(frame_text)

            filename = f"{frame_number:06d}.bin"

            filepath = os.path.join(
                self.dataset_folder,
                filename
            )

            if not os.path.exists(filepath):

                messagebox.showerror(
                    "File Not Found",
                    f"Could not find:\n{filepath}"
                )

                return

            # --------------------------------------------------
            # KITTI LiDAR format:
            #
            # X Y Z Intensity
            # --------------------------------------------------

            data = np.fromfile(
                filepath,
                dtype=np.float32
            )

            data = data.reshape(
                -1,
                4
            )

            # Store X Y Z

            self.raw_points = data[:, :3]

            self.frame_number = frame_number

            # Reset previous results

            self.adaptive_map = None
            self.ground_map = None
            self.obstacle_map = None

            # --------------------------------------------------
            # Status
            # --------------------------------------------------

            self.status_label.config(
                text=(
                    f"Loaded frame "
                    f"{frame_number:06d} | "
                    f"Points: "
                    f"{len(self.raw_points):,}"
                )
            )

            # --------------------------------------------------
            # Display Raw LiDAR
            # --------------------------------------------------

            self.axes[0].clear()

            self.axes[0].scatter(
                self.raw_points[:, 0],
                self.raw_points[:, 1],
                s=1
            )

            self.axes[0].set_title(
                "Raw LiDAR"
            )

            self.axes[0].set_xlabel(
                "X (m)"
            )

            self.axes[0].set_ylabel(
                "Y (m)"
            )

            # Clear remaining panels

            self.axes[1].clear()
            self.axes[2].clear()
            self.axes[3].clear()

            self.axes[1].set_title(
                "Adaptive 2.5D Map"
            )

            self.axes[2].set_title(
                "Height Map"
            )

            self.axes[3].set_title(
                "Resolution Map"
            )

            self.figure.tight_layout()

            self.canvas.draw()

        except Exception as error:

            messagebox.showerror(
                "Load Error",
                str(error)
            )

    # ==========================================================
    # ADAPTIVE 2.5D MODEL
    # ==========================================================

    def run_adaptive_model(self):

        if self.raw_points is None:

            messagebox.showwarning(
                "No LiDAR",
                "Load a LiDAR frame first."
            )

            return

        try:

            points = self.raw_points

            x = points[:, 0]
            y = points[:, 1]
            z = points[:, 2]

            # --------------------------------------------------
            # Distance from LiDAR sensor
            # --------------------------------------------------

            distance = np.sqrt(
                x * x + y * y
            )

            # --------------------------------------------------
            # Adaptive resolution
            #
            # Near  -> 5 cm
            # Middle -> 10 cm
            # Far -> 20 cm
            # --------------------------------------------------

            resolution = np.where(
                distance < 10.0,
                0.05,
                np.where(
                    distance < 25.0,
                    0.10,
                    0.20
                )
            )

            # --------------------------------------------------
            # Common origin
            # --------------------------------------------------

            origin_x = np.min(x)
            origin_y = np.min(y)

            # --------------------------------------------------
            # Cell coordinates
            # --------------------------------------------------

            cell_x = np.floor(
                (x - origin_x) / resolution
            ).astype(
                np.int64
            )

            cell_y = np.floor(
                (y - origin_y) / resolution
            ).astype(
                np.int64
            )

            # --------------------------------------------------
            # Unique adaptive cells
            # --------------------------------------------------

            cell_data = np.column_stack(
                (
                    cell_x,
                    cell_y,
                    resolution
                )
            )

            unique_cells, inverse = np.unique(
                cell_data,
                axis=0,
                return_inverse=True
            )

            # --------------------------------------------------
            # Average Z for each cell
            # --------------------------------------------------

            height_sum = np.bincount(
                inverse,
                weights=z
            )

            count = np.bincount(
                inverse
            )

            mean_z = (
                height_sum / count
            )

            # --------------------------------------------------
            # Convert cell coordinates to X/Y
            # --------------------------------------------------

            cell_resolution = unique_cells[:, 2]

            cell_center_x = (
                origin_x
                +
                (
                    unique_cells[:, 0] + 0.5
                )
                *
                cell_resolution
            )

            cell_center_y = (
                origin_y
                +
                (
                    unique_cells[:, 1] + 0.5
                )
                *
                cell_resolution
            )

            # --------------------------------------------------
            # Final adaptive map
            #
            # Column 0 = X
            # Column 1 = Y
            # Column 2 = Mean Z
            # Column 3 = Resolution
            # --------------------------------------------------

            self.adaptive_map = np.column_stack(
                (
                    cell_center_x,
                    cell_center_y,
                    mean_z,
                    cell_resolution
                )
            )

            # ==================================================
            # STATISTICS
            # ==================================================

            fine = np.sum(
                self.adaptive_map[:, 3] == 0.05
            )

            medium = np.sum(
                self.adaptive_map[:, 3] == 0.10
            )

            coarse = np.sum(
                self.adaptive_map[:, 3] == 0.20
            )

            adaptive_cells = len(
                self.adaptive_map
            )

            # --------------------------------------------------
            # Fixed 5 cm representation
            # --------------------------------------------------

            fixed_resolution = 0.05

            fixed_x = np.floor(
                (x - origin_x)
                /
                fixed_resolution
            ).astype(
                np.int64
            )

            fixed_y = np.floor(
                (y - origin_y)
                /
                fixed_resolution
            ).astype(
                np.int64
            )

            fixed_cells = len(
                np.unique(
                    np.column_stack(
                        (
                            fixed_x,
                            fixed_y
                        )
                    ),
                    axis=0
                )
            )

            # --------------------------------------------------
            # Cell reduction
            # --------------------------------------------------

            reduction = (
                (
                    fixed_cells
                    -
                    adaptive_cells
                )
                /
                fixed_cells
                *
                100
            )

            # ==================================================
            # PANEL 1 - ADAPTIVE 2.5D
            # ==================================================

            self.axes[0].clear()

            self.axes[0].scatter(
                self.adaptive_map[:, 0],
                self.adaptive_map[:, 1],
                c=self.adaptive_map[:, 2],
                s=2
            )

            self.axes[0].set_title(
                "Adaptive 2.5D Map"
            )

            self.axes[0].set_xlabel(
                "X (m)"
            )

            self.axes[0].set_ylabel(
                "Y (m)"
            )

            # ==================================================
            # PANEL 2 - HEIGHT MAP
            # ==================================================

            self.axes[1].clear()

            self.axes[1].scatter(
                self.adaptive_map[:, 0],
                self.adaptive_map[:, 1],
                c=self.adaptive_map[:, 2],
                s=4
            )

            self.axes[1].set_title(
                "2.5D Height Map"
            )

            self.axes[1].set_xlabel(
                "X (m)"
            )

            self.axes[1].set_ylabel(
                "Y (m)"
            )

            # ==================================================
            # PANEL 3 - RESOLUTION
            # ==================================================

            self.axes[2].clear()

            self.axes[2].scatter(
                self.adaptive_map[:, 0],
                self.adaptive_map[:, 1],
                c=self.adaptive_map[:, 3],
                s=4
            )

            self.axes[2].set_title(
                "Adaptive Resolution"
            )

            self.axes[2].set_xlabel(
                "X (m)"
            )

            self.axes[2].set_ylabel(
                "Y (m)"
            )

            # ==================================================
            # PANEL 4 - STATISTICS
            # ==================================================

            self.axes[3].clear()

            self.axes[3].axis(
                "off"
            )

            statistics = (
                f"FRAME {self.frame_number:06d}\n\n"

                f"Original Points\n"
                f"{len(points):,}\n\n"

                f"Fixed 5 cm Cells\n"
                f"{fixed_cells:,}\n\n"

                f"Adaptive Cells\n"
                f"{adaptive_cells:,}\n\n"

                f"Reduction\n"
                f"{reduction:.2f}%\n\n"

                f"Fine 5 cm\n"
                f"{fine:,}\n\n"

                f"Medium 10 cm\n"
                f"{medium:,}\n\n"

                f"Coarse 20 cm\n"
                f"{coarse:,}"
            )

            self.axes[3].text(
                0.05,
                0.95,
                statistics,
                transform=self.axes[3].transAxes,
                verticalalignment="top",
                fontsize=12
            )

            self.figure.tight_layout()

            self.canvas.draw()

            self.status_label.config(
                text=(
                    f"Adaptive mapping complete | "
                    f"Fixed: {fixed_cells:,} | "
                    f"Adaptive: {adaptive_cells:,} | "
                    f"Reduction: {reduction:.2f}%"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Adaptive Model Error",
                str(error)
            )

    # ==========================================================
    # TERRAIN ANALYSIS
    # ==========================================================

    def terrain_analysis(self):

        if self.adaptive_map is None:

            messagebox.showwarning(
                "No Results",
                "Run the adaptive model first."
            )

            return

        try:

            data = self.adaptive_map

            x = data[:, 0]
            y = data[:, 1]
            z = data[:, 2]

            # --------------------------------------------------
            # Terrain threshold
            # --------------------------------------------------

            terrain_threshold = 0.30

            # --------------------------------------------------
            # Local neighbourhood grid
            # --------------------------------------------------

            grid_size = 0.5

            grid_x = np.floor(
                x / grid_size
            ).astype(
                np.int64
            )

            grid_y = np.floor(
                y / grid_size
            ).astype(
                np.int64
            )

            # --------------------------------------------------
            # Store minimum height
            # --------------------------------------------------

            local_minimum = {}

            for i in range(len(z)):

                key = (
                    grid_x[i],
                    grid_y[i]
                )

                if key not in local_minimum:

                    local_minimum[key] = z[i]

                elif z[i] < local_minimum[key]:

                    local_minimum[key] = z[i]

            # --------------------------------------------------
            # Classification
            # --------------------------------------------------

            ground_indices = []
            obstacle_indices = []

            for i in range(len(z)):

                key = (
                    grid_x[i],
                    grid_y[i]
                )

                minimum_height = (
                    local_minimum[key]
                )

                height_difference = (
                    z[i]
                    -
                    minimum_height
                )

                if (
                    height_difference
                    <= terrain_threshold
                ):

                    ground_indices.append(i)

                else:

                    obstacle_indices.append(i)

            # --------------------------------------------------
            # Store maps
            # --------------------------------------------------

            self.ground_map = data[
                ground_indices
            ]

            self.obstacle_map = data[
                obstacle_indices
            ]

            # --------------------------------------------------
            # Clear panels
            # --------------------------------------------------

            for ax in self.axes:

                ax.clear()

            # ==================================================
            # PANEL 1
            # ==================================================

            self.axes[0].scatter(
                x,
                y,
                c=z,
                s=2
            )

            self.axes[0].set_title(
                "Adaptive 2.5D"
            )

            # ==================================================
            # PANEL 2
            # ==================================================

            self.axes[1].scatter(
                x,
                y,
                c=z,
                s=3
            )

            self.axes[1].set_title(
                "Height Map"
            )

            # ==================================================
            # PANEL 3 - GROUND
            # ==================================================

            if len(self.ground_map) > 0:

                self.axes[2].scatter(
                    self.ground_map[:, 0],
                    self.ground_map[:, 1],
                    s=3
                )

            self.axes[2].set_title(
                "Ground / Terrain"
            )

            # ==================================================
            # PANEL 4 - OBSTACLES
            # ==================================================

            if len(self.obstacle_map) > 0:

                self.axes[3].scatter(
                    self.obstacle_map[:, 0],
                    self.obstacle_map[:, 1],
                    s=4
                )

            self.axes[3].set_title(
                "Obstacles"
            )

            # --------------------------------------------------
            # Labels
            # --------------------------------------------------

            for ax in self.axes:

                ax.set_xlabel(
                    "X (m)"
                )

                ax.set_ylabel(
                    "Y (m)"
                )

            self.figure.tight_layout()

            self.canvas.draw()

            self.status_label.config(
                text=(
                    f"Terrain analysis complete | "
                    f"Ground = "
                    f"{len(self.ground_map):,} | "
                    f"Obstacles = "
                    f"{len(self.obstacle_map):,}"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Terrain Error",
                str(error)
            )

    # ==========================================================
    # FINAL INTEGRATED MAP
    # ==========================================================

    def final_integrated_map(self):

        if self.adaptive_map is None:

            messagebox.showwarning(
                "No Results",
                "Run the adaptive model first."
            )

            return

        if (
            self.ground_map is None
            or
            self.obstacle_map is None
        ):

            messagebox.showwarning(
                "Terrain Analysis Required",
                "Run Terrain Analysis first."
            )

            return

        try:

            # --------------------------------------------------
            # Clear all panels
            # --------------------------------------------------

            for ax in self.axes:

                ax.clear()

            # ==================================================
            # PANEL 1 - FINAL 2.5D MAP
            # ==================================================

            self.axes[0].scatter(
                self.adaptive_map[:, 0],
                self.adaptive_map[:, 1],
                c=self.adaptive_map[:, 2],
                s=3
            )

            self.axes[0].set_title(
                "Final Adaptive 2.5D"
            )

            # ==================================================
            # PANEL 2 - VARIABLE RESOLUTION
            # ==================================================

            self.axes[1].scatter(
                self.adaptive_map[:, 0],
                self.adaptive_map[:, 1],
                c=self.adaptive_map[:, 3],
                s=3
            )

            self.axes[1].set_title(
                "Variable Resolution"
            )

            # ==================================================
            # PANEL 3 - GROUND + OBSTACLES
            # ==================================================

            if len(self.ground_map) > 0:

                self.axes[2].scatter(
                    self.ground_map[:, 0],
                    self.ground_map[:, 1],
                    s=3,
                    label="Ground"
                )

            if len(self.obstacle_map) > 0:

                self.axes[2].scatter(
                    self.obstacle_map[:, 0],
                    self.obstacle_map[:, 1],
                    s=8,
                    label="Obstacle"
                )

            self.axes[2].set_title(
                "Ground + Obstacles"
            )

            self.axes[2].legend()

            # ==================================================
            # PANEL 4 - FINAL SUMMARY
            # ==================================================

            self.axes[3].axis(
                "off"
            )

            total = len(
                self.adaptive_map
            )

            ground = len(
                self.ground_map
            )

            obstacles = len(
                self.obstacle_map
            )

            # Resolution counts

            fine = np.sum(
                self.adaptive_map[:, 3] == 0.05
            )

            medium = np.sum(
                self.adaptive_map[:, 3] == 0.10
            )

            coarse = np.sum(
                self.adaptive_map[:, 3] == 0.20
            )

            # --------------------------------------------------
            # Summary text
            # --------------------------------------------------

            summary = (
                "FINAL LiDAR PERCEPTION\n\n"

                f"Frame\n"
                f"{self.frame_number:06d}\n\n"

                f"LiDAR Points\n"
                f"{len(self.raw_points):,}\n\n"

                f"Adaptive Cells\n"
                f"{total:,}\n\n"

                f"Fine 5 cm\n"
                f"{fine:,}\n\n"

                f"Medium 10 cm\n"
                f"{medium:,}\n\n"

                f"Coarse 20 cm\n"
                f"{coarse:,}\n\n"

                f"Ground\n"
                f"{ground:,}\n\n"

                f"Obstacles\n"
                f"{obstacles:,}"
            )

            self.axes[3].text(
                0.05,
                0.95,
                summary,
                transform=self.axes[3].transAxes,
                verticalalignment="top",
                fontsize=12
            )

            # --------------------------------------------------
            # Labels
            # --------------------------------------------------

            for ax in self.axes[:3]:

                ax.set_xlabel(
                    "X (m)"
                )

                ax.set_ylabel(
                    "Y (m)"
                )

            self.figure.tight_layout()

            self.canvas.draw()

            self.status_label.config(
                text=(
                    f"FINAL MAP | "
                    f"Adaptive = {total:,} | "
                    f"Ground = {ground:,} | "
                    f"Obstacles = {obstacles:,}"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Final Map Error",
                str(error)
            )

    # ==========================================================
    # SAVE RESULTS
    # ==========================================================

    def save_results(self):

        if self.adaptive_map is None:

            messagebox.showwarning(
                "No Results",
                "Run the adaptive model first."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Save LiDAR Results",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png")
            ]
        )

        if not filename:

            return

        try:

            self.figure.savefig(
                filename,
                dpi=300,
                bbox_inches="tight"
            )

            messagebox.showinfo(
                "Saved",
                "LiDAR results saved successfully."
            )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )


# ==============================================================
# START APPLICATION
# ==============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = LiDARApp(root)

    root.mainloop()