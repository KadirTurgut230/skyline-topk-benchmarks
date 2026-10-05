# skyline-topk-benchmarks
This project was developed to perform Skyline (finding the best options that are not dominated by other records) and Top-K (finding the highest-scoring records based on a specific criterion) analyses on multi-dimensional datasets. The main goal is to test and compare the speed, memory (RAM) usage, and processing efficiency of different data mining algorithms.

Key Features

Data Generation: Random multi-dimensional datasets are dynamically generated using LMDB and PostgreSQL (PL/pgSQL) infrastructures.
Performance Measurement: While the algorithms are running, the total execution time, instantaneous and peak RAM usage, time to find the first result (response time), and the number of record comparisons are measured in detail.
Visualization: All obtained test results are converted into comparative line charts and matrix tables using Matplotlib.

Skyline Algorithms

NNL (Naive Nested Loop): This is the simplest method that compares each record with all other records one by one.
BNL (Block Nested Loop): It opens a processing window with a specific capacity in RAM and uses temporary files for data that does not fit, thereby reducing the number of loops.
D&C (Divide and Conquer): It sorts the data, divides it into parts, and merges them after finding the Skyline results of these subsets.
SFS (Sort Filter Skyline): It first sorts the data based on its distance to the origin (zero point), and then performs the filtering process.
B-Tree: It indexes the data according to its dimensions using a B-Tree structure, preparing and supporting the data for the SFS method.
BBS (Branch and Bound Skyline): It divides the data space into bounding boxes (MBR) using R-Tree logic, thus demonstrating high performance by pruning useless branches from the very beginning.

Top-K Querying Module : In addition to the Skyline analysis, the project also includes an SQL-based Top-K analysis module running on PostgreSQL. It creates a database table of a parametrically desired size and fills it with random data. It normalizes multi-dimensional data according to given weights (grades) and calculates a final score for each record. It then sorts the records according to this score and retrieves the best K results determined by the user.

Testing and Comparison

The bitirme_test.py and bitirme_test_2.py modules in the project automate the testing processes. These files put the algorithms into a race simultaneously under the specified data size, capacity, or feature limits. After the execution, the system checks whether the results match each other to verify the accuracy of the algorithms, and performance reports are exported as graphs.
