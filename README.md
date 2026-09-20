\# Adaptive Variable-Resolution 2.5D LiDAR Mapping for Dynamic Environment Perception



A Python prototype for representing automotive LiDAR point clouds using an adaptive variable-resolution 2.5D map.



The project changes the spatial resolution according to the distance of LiDAR points from the sensor. Nearby regions are represented using finer cells, while farther regions use larger cells. The goal is to reduce the number of spatial cells required while retaining elevation information.



\---



\## Overview



LiDAR sensors produce dense 3D point clouds that contain information about the surrounding environment.



A common approach is to represent the environment using a fixed-size grid. Although this is simple, the same resolution is then used for both nearby and distant regions.



This project investigates a simple alternative:



> Use higher spatial resolution near the sensor and progressively lower resolution farther away.



The current prototype uses three distance-based resolution levels:



| Distance | Resolution |

|---|---:|

| < 10 m | 5 cm |

| 10–25 m | 10 cm |

| >= 25 m | 20 cm |



The resulting representation retains X and Y position together with Z elevation, forming a 2.5D representation.



\---



\## Problem



Automotive LiDAR can generate a large number of points in every scan.



Using a fine grid over the complete sensing region can create many spatial cells, including in distant regions where the same level of detail may not always be necessary.



The project investigates whether a variable-resolution representation can reduce the number of occupied spatial cells compared with a fixed 5 cm grid.



\---



\## Proposed Approach



The implemented pipeline is:



```text

LiDAR Point Cloud

&#x20;       |

&#x20;       v

Point Cloud Loading

&#x20;       |

&#x20;       v

Distance Calculation

&#x20;       |

&#x20;       v

Resolution Selection

&#x20;       |

&#x20;       +---- < 10 m ------> 5 cm

&#x20;       |

&#x20;       +---- 10–25 m -----> 10 cm

&#x20;       |

&#x20;       +---- >= 25 m -----> 20 cm

&#x20;       |

&#x20;       v

Adaptive 2.5D Grid

&#x20;       |

&#x20;       v

Z Elevation Aggregation

&#x20;       |

&#x20;       v

Terrain / Obstacle Analysis

&#x20;       |

&#x20;       v

Visualization

&#x20;       |

&#x20;       v

Benchmarking



For every LiDAR point, the horizontal distance from the sensor is calculated using:



distance = sqrt(X² + Y²)



The appropriate grid resolution is then selected based on this distance.



Points belonging to the same adaptive cell are grouped together and their Z values are averaged.



What is 2.5D in this project?



The representation uses:



X → horizontal position

Y → horizontal position

Z → elevation



Unlike a full 3D voxel representation, the map does not divide the environment into multiple vertical layers.



Instead, each spatial cell stores an elevation value.



This provides a simpler representation while retaining useful height information.



Adaptive Resolution



The current prototype uses three resolution bands.



Fine resolution

Distance < 10 m

Grid size = 0.05 m



This provides more detail in the region close to the sensor.



Medium resolution

10 m <= Distance < 25 m

Grid size = 0.10 m

Coarse resolution

Distance >= 25 m

Grid size = 0.20 m



The 5 cm, 10 cm and 20 cm values are prototype settings used for the current experimental evaluation. They have not been established as globally optimal values.



Terrain Analysis



The prototype also contains a basic geometric terrain analysis stage.



A 0.5 m analysis grid is used to estimate the local minimum elevation. A 0.30 m height threshold is then used to separate points close to the local minimum from higher points.



This module is a geometric prototype.



It is not a trained semantic segmentation or object detection model.



Experimental Evaluation



The system was evaluated using 10 consecutive automotive LiDAR frames.



Dataset

Frames tested:       10

Total LiDAR points:  1,235,429

Average/frame:       123,543 points



The proposed adaptive representation was compared with a fixed 5 cm representation.



Results

Metric	Result

Average fixed cells/frame	63,323

Average adaptive cells/frame	46,778

Average reduction	26.13%

Average fine cells	24,790

Average medium cells	15,232

Average coarse cells	6,757

Average processing time	590.02 ms/frame

Average peak Python memory	14.02 MB



The adaptive representation reduced the average number of occupied spatial cells from:



63,323



to:



46,778



This corresponds to an average:



26.13% reduction



in spatial representation for the tested frames.



Important interpretation



The 26.13% value represents a reduction in the number of occupied spatial cells.



It should not be interpreted as:



26.13% RAM saving

26.13% accuracy improvement

26.13% processing-speed improvement



The benchmark measured an average processing time of 590.02 ms per frame. Real-time performance has not been established.



Frame-Level Results

Frame	Points	Fixed Cells	Adaptive Cells	Reduction

000000	124,668	67,018	49,481	26.17%

000001	124,605	66,233	48,836	26.27%

000002	124,478	65,137	48,165	26.06%

000003	124,167	64,229	47,446	26.13%

000004	123,969	63,353	46,931	25.92%

000005	123,924	62,826	46,405	26.14%

000006	123,373	61,867	45,668	26.18%

000007	122,765	61,320	45,192	26.30%

000008	122,123	60,807	44,899	26.16%

000009	121,357	60,438	44,756	25.95%



The reduction remains close to 26% across the tested frames.



Implementation



The prototype is implemented in Python.



Main technologies

Python 3.11

NumPy

Open3D

Matplotlib

Pandas

SciPy

scikit-learn

Conda



The project contains:



Adaptive-Variable-Resolution-2.5D-LiDAR-Mapping/

│

├── README.md

├── requirements.txt

│

├── src/

│   ├── final\_lidar\_model.py

│   ├── final\_benchmark.py

│   └── generate\_plots.py

│

├── dataset/

│   └── LiDAR data

│

├── results/

│   ├── benchmark\_results.csv

│   ├── benchmark\_summary.txt

│   └── figures/

│       ├── fixed\_vs\_adaptive\_cells.png

│       ├── representation\_reduction.png

│       ├── resolution\_distribution.png

│       └── processing\_time.png

│

├── report/

│   └── technical\_report.pdf

│

└── demo/

Running the Project

1\. Create the Conda environment

conda create -n lidar python=3.11



Activate it:



conda activate lidar

2\. Install the required packages

pip install -r requirements.txt

3\. Run the main application



From the project root:



python src/final\_lidar\_model.py



The GUI allows the user to:



Load LiDAR data

Run the adaptive model

Perform terrain analysis

Generate the final integrated map

Save results

Running the Benchmark



Run:



python src/final\_benchmark.py



The benchmark generates:



results/benchmark\_results.csv

results/benchmark\_summary.txt



The benchmark records:



LiDAR point count

Fixed-resolution cell count

Adaptive cell count

Representation reduction

Fine/medium/coarse cell distribution

Processing time

Peak Python memory

Generating the Graphs



Run:



python src/generate\_plots.py



The following figures are generated:



results/figures/

├── fixed\_vs\_adaptive\_cells.png

├── representation\_reduction.png

├── resolution\_distribution.png

└── processing\_time.png

Research Background



The project is related to research in two areas:



2.5D LiDAR Mapping



Aldibaja and Suganuma presented a graph-SLAM-based 2.5D LiDAR mapping approach for autonomous vehicles using intensity and elevation information.



Variable-Resolution Mapping



O'Meadhra, Tabib and Michael investigated variable-resolution occupancy mapping using Gaussian mixture models and discussed limitations associated with fixed spatial discretization.



The current project uses these areas as research foundations while implementing a simpler distance-based variable-resolution prototype.



Limitations



The current implementation has several limitations:



Resolution selection is mainly based on distance.

The current 5/10/20 cm settings have not been established as globally optimal.

Only 10 LiDAR frames were used for the current benchmark.

Ground-truth mapping accuracy has not been evaluated.

Trained semantic segmentation is not implemented.

Trained dynamic-object detection is not implemented.

Real-time performance has not been demonstrated.

A fixed-versus-adaptive RAM comparison has not been performed.

The current terrain classifier is geometric rather than AI-based.

The current implementation is a prototype and requires further optimization.

Future Work



Several extensions are planned for future versions.



1\. Geometry-aware resolution



Resolution could be selected using local terrain variation and geometric complexity instead of distance alone.



2\. Uncertainty-aware mapping



Sensor uncertainty and map uncertainty could be included in the resolution decision.



3\. Semantic perception



A trained perception model could identify roads, vehicles, pedestrians and other objects.



4\. Dynamic-object handling



Moving objects could be treated separately from static environment structures.



5\. Performance optimization



The implementation could be optimized using vectorization, parallel processing or GPU acceleration.



6\. Larger evaluation



Future experiments should use more sequences and different environments and compare:



Representation size

Processing time

Memory consumption

Mapping accuracy

Perception accuracy

Technical Report



The complete technical report is available here:



Technical Report



The report contains the methodology, experimental setup, benchmark results, limitations and future work in greater detail.



Project Status



Current status: Prototype completed and experimentally evaluated



Implemented:



&#x20;LiDAR point-cloud input

&#x20;Distance-based adaptive resolution

&#x20;2.5D representation

&#x20;Elevation aggregation

&#x20;Terrain/obstacle prototype

&#x20;Visualization GUI

&#x20;Fixed-resolution comparison

&#x20;10-frame benchmark

&#x20;Result CSV

&#x20;Benchmark graphs

&#x20;Technical report



Future development:



&#x20;Geometry-aware adaptive resolution

&#x20;Uncertainty-aware resolution

&#x20;Semantic segmentation

&#x20;Dynamic-object detection

&#x20;Ground-truth accuracy evaluation

&#x20;Memory comparison

&#x20;Real-time optimization

&#x20;Larger dataset evaluation

References

M. Aldibaja and Y. Suganuma, “Graph SLAM-Based 2.5D LIDAR Mapping Module for Autonomous Vehicles,” Remote Sensing, vol. 13, no. 24, 5066, 2021.

C. O'Meadhra, A. Tabib, and A. Michael, “Variable Resolution Occupancy Mapping Using Gaussian Mixture Models,” IEEE Robotics and Automation Letters, 2019. DOI: 10.1109/LRA.2018.2889348.

Author



Tharun S.S.



B.Tech – Computer and Communication Engineering

Amrita Vishwa Vidyapeetham, Coimbatore



2026

