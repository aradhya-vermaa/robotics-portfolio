# Robotics Engineering Portfolio
**Aradhya Verma** | University of Wisconsin–Madison  
[Email](mailto:verma48@wisc.edu) • [LinkedIn](https://linkedin.com)

Autonomous systems, marine robotics hardware, and robotic manipulation portfolio featuring rapid prototyping, subsea avionics integration, computer vision perception, and closed-loop kinematic control.

---

## 1. FloatForm: Modular Swarm Robotic Boats
*Marine Robotics Laboratory | June – July 2026*

Autonomous surface vessel (ASV) swarm research platform designed for multi-agent self-assembly, relative pose tracking, and passive magnetic docking.

### Relative Pose Tracking & Autonomous Docking Demo
![ASV Latching Test](asvlatchingtest.gif)

* **Full-Stack Hardware Bring-Up:** Rapid-prototyped and built 5 autonomous marine vessels from scratch, fabricating 3D-printed chassis parts, integrating Li-ion power, and bringing up low-level motor drive electronics.
* **Empirical Propulsion Profiling:** Built a test rig using force-load instrumentation to characterize dynamic thrust outputs across all vector axes, identifying motor deadbands and non-linearities to inform closed-loop control.
* **Perception & Latching Envelope Mapping:** Deployed an OpenCV/AprilTag optical tracking pipeline to track multi-boat interaction dynamics, analyzing experimental data in MATLAB to discover the 86° / 15.2 cm capture boundary for zero-power magnetic docking.

### Hardware Fabrication & Docking Acceptance Characterization
<p align="center">
  <img src="micro_asv.png" width="48%" />
  <img src="Scatterplot.png" width="48%" />
</p>

* **Perception Pipeline:** [`latching_area.py`](./latching_area.py)
* **Analysis & Visualization Script:** [`Scatterplot.m`](./Scatterplot.m)
* **Empirical Trial Dataset:** [`experiment_data.csv`](./experiment_data.csv)
* **Additional Hull Views:** [`micro_asv2.png`](./micro_asv2.png)

---

## 2. BlueROV Subsea Platform & Custom Avionics Integration
*Marine Robotics Laboratory | August 2026 – Present*

Subsea Remotely Operated Vehicle (ROV) configured for high-reliability pressure vessel packaging, telemetry communication, and auxiliary payload integration.

### CAD Chassis Packaging & Hardware Integration
![BlueROV Integration](BluROV.png)

* **Constrained CAD Packaging:** Designed a multi-tier custom electronics chassis in CAD to pack a Navigator flight stack, Arduino, high-current ESCs, battery packs, and subsea optics into a compact cylindrical pressure hull.
* **Dense Avionics & Harnessing:** Integrated the complete internal electrical system, resolving packaging clashes, routing high-current motor buses, and establishing tethered surface-to-vehicle telemetry via high-speed Ethernet bridges.
* **Hydrostatic Sealing & Leak Isolation:** Overcame water-ingress failures through repeated submersion and overnight static soak tests; systematically debugged cable penetrators, tuned O-ring compression tolerances, and eliminated seal failures to achieve a verified waterproof vehicle.
* **Telemetry & Motor Calibration:** Calibrated motor response mappings and authored custom ROS 2 telemetry nodes to stream live PWM actuation data and monitor dynamic motor speed curves ahead of pool trials.

---

## 3. Autonomous Pick-and-Place Manipulation (UR5e Capstone)
*Robotics Simulation Capstone | 2025*

Autonomous color-based sorting pipeline utilizing a 6-DOF UR5e robotic manipulator and wrist-mounted RGB camera in Webots.

### Closed-Loop Sorting & Manipulation Demo
![UR5e Simulation Capstone](Capstone.gif)

* **Computer Vision Pipeline:** Implemented color segmentation and centroid detection via a wrist-mounted camera stream to trigger real-time grasp poses.
* **Kinematics & Trajectory Control:** Derived and implemented forward/inverse kinematics (FK/IK) and Jacobian-based trajectory planning to execute smooth pick-and-place paths.
* **Closed-Loop Automation:** Integrated sensing, grasp validation, and trajectory execution loops to evaluate task success rates and system fault handling across repeated simulation trials.

### Simulation Scripts & Controllers
* **Inverse Kinematics Solver:** [`arm_ik.py`](./arm_ik.py)
* **Kinematics Helper Functions:** [`kinematic_helpers.py`](./kinematic_helpers.py)
* **Sorting Controllers:** [`color_sort_controller.py`](./color_sort_controller.py) | [`color_sort_controller.c`](./color_sort_controller.c)
* **Webots Simulation World:** [`color_sorting.wbt`](./color_sorting.wbt)
```[cite: 1, 2, 5, 6, 7, 13]

---

### How to apply this right now:
1. Click on **`README.md`** in your repository file list[cite: 13].
2. Click the **pencil icon** (Edit this file).
3. Select all the existing text, hit delete, and paste this block into the file.
4. Scroll down and click the green **Commit changes...** button[cite: 12].
