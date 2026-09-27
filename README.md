# Robotics Engineering Portfolio
**Aradhya Verma** | University of Wisconsin–Madison  
+1 (608)-217-8658 • [verma48@wisc.edu](mailto:verma48@wisc.edu)

Autonomous systems, marine robotics hardware, and robotic manipulation portfolio featuring rapid prototyping, subsea avionics integration, computer vision perception, and closed-loop kinematic control.

---

## 1. FloatForm: Modular Swarm Robotic Boats
*Marine Robotics Laboratory | June – July 2026*

Autonomous surface vessel (ASV) swarm research platform designed for multi-agent self-assembly, relative pose tracking, and passive magnetic docking.

| Visual | System Architecture & Engineering Rigor |
| :---: | :--- |
| <img src="micro_asv.png" width="380" /> | **Full-Stack Hardware Fabrication**<br>• Rapid-prototyped and fabricated 5 autonomous marine vessels from scratch.<br>• 3D-printed custom modular hull enclosures, motor brackets, and stabilizing fins.<br>• Packaged internal lithium-ion battery units, power distribution, and microcontroller avionics. |
| <img src="micro_asv2.png" width="380" /> | **Actuation, Latching & Thrust Profiling**<br>• Integrated a central motorized magnetic latching mechanism for zero-power rigid docking.<br>• Instrumented directional thrusters with force sensors to profile static and dynamic thrust.<br>• Identified motor deadbands and actuation non-linearities across all planar vector axes. |
| <img src="asvlatchingtest.gif" width="380" /> | **Optical Tracking & Docking Kinematics**<br>• Developed an overhead OpenCV pipeline using AprilTag markers on approaching vessels.<br>• Tracked real-time relative distance, coordinate displacement, and angular bearing.<br>• Extracted continuous docking kinematics to isolate entry conditions for passive latching. |
| <img src="Scatterplot.png" width="380" /> | **Capture Envelope Modeling (MATLAB)**<br>• Analyzed multi-trial experimental tracking runs to define the passive capture boundary.<br>• Mapped the valid zero-thrust latching sector to an 86° angle and 15.2 cm radius.<br>• Scripts & Data: [`Scatterplot.m`](./Scatterplot.m) • [`latching_area.py`](./latching_area.py) • [`experiment_data.csv`](./experiment_data.csv) |

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
