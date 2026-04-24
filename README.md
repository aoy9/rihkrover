# RIHK Rover Project  
### The RIHK Rover team was a part of EPIC Campus' Aerospace program that competed in the 2026 Colorado Space Grant Consortium's Robotics Challenge. The competition took place in the Great Sand Dunes National Park, where autonomous rovers built by competing teams prove their capabilities by autonomously navigating through obstacle courses that simulate extraterrestrial terrain. The following is a detailed overview of the hardware and software designs of Team RIHK's design.  
## Hardware Architecture

### The rover's hardware is designed for agility and real-time responsiveness, utilizing a rear-wheel-drive (RWD) differential setup.

### Computing & Control
* **On-board Microcomputer:** Raspberry Pi 4 Model B (Handles sensor data acquisition and motor command relay).
* **Companion Computer:** Off-board laptop/desktop (Handles heavy YOLOv11 vision processing, SLAM, and Nav2 path planning).

### Sensors
* **LiDAR:** RPLiDAR A1M8 (Provides 360° 2D environmental scanning).
* **Camera:** Raspberry Pi Camera Module 2 (Mounted with a specific downward pitch for terrain observation).
* **IMU:** BNO085 (Provides drift-free, high-accuracy orientation and heading data).

### Actuation
* **Motor Controllers:** 2x ServoCity 1x20A Motor Controllers.
* **Motors:** 2x ServoCity 624RPM Premium Planetary Gear Motors.

---

## Software Architecture

### The software stack is built entirely on **ROS 2 (Humble / Jazzy)**, leveraging a node-based communication network to integrate traditional robotic navigation with modern deep-learning computer vision.

### 1. SLAM & Localization (Odometry without Encoders)
Because the rover operates without physical wheel encoders, it relies entirely on a robust sensor-fusion pipeline for Simultaneous Localization and Mapping (SLAM):
* **LiDAR Odometry (`rf2o`):** Sequential laser scans from the RPLiDAR are matched to calculate the robot's X and Y translation across the floor.
* **Sensor Fusion (EKF):** An Extended Kalman Filter (`robot_localization`) merges the physical translation from the `rf2o` node with the highly accurate absolute rotation (Yaw) from the BNO085 IMU. This eliminates rotational drift and provides a rock-solid coordinate frame even if the rear wheels slip.
* **Mapping:** The fused odometry and LiDAR scans are used to generate real-time 2D occupancy grids of the environment.

### 2. Vision & Perception (YOLOv11)
To handle obstacles that the 2D LiDAR might miss (e.g., low-lying rocks or negative obstacles), the rover employs a custom-trained **YOLOv11** model powered by Ultralytics.
* **Distributed Processing:** Raw video feeds are compressed and sent from the Pi to the companion computer, which runs the YOLOv11 inference node to maintain high framerates.
* **Kinematic Distance Estimation:** Using the known mounting height and downward angle of the Pi Camera, the system mathematically projects 2D bounding boxes into 3D space, estimating the real-world distance to detected rocks and obstacles.

### 3. Autonomous Navigation (Nav2)
The rover utilizes the **Nav2** (Open Navigation) framework to autonomously move through the environment.
* **Dynamic Costmaps:** Filtered LiDAR data constructs the base obstacle layer.
* **Risk Map Integration:** The 3D coordinate estimations from the YOLOv11 vision node are injected directly into the Nav2 local and global costmaps as point clouds. This multi-sensor integration ensures the path planner explicitly routes around visually identified hazards.
* **Custom Controllers:** Velocity smoothers and motor controller parameters prevent aggressive acceleration, ensuring the planetary gear motors do not break traction during navigation.

