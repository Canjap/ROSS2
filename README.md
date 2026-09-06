# ROSS2 (Remote Observation & Swarm System v2)

**ROSS2** is a complete architectural redesign and evolution of the original **ROSS** project. While maintaining the core objective of **remote observation**, ROSS2 completely overhauls the system framework to introduce a distributed **Server + Swarm** topology tailored for tactical operations and search-and-rescue environments.

---

## Project Overview

In hazardous scenarios—such as active building fires or structural collapses—gaining rapid situational awareness without exposing first responders to extreme risk is critical. 

ROSS2 addresses this challenge by deploying a coordinated swarm of low-cost, compact mobile robots into unsafe structures to gather real-time video feeds and sensory telemetry. The system decouples high-level coordination and external network bridging from low-level swarm operation, allowing autonomous ground units to operate independently while remaining accessible to authorized remote operators.

---

## System Architecture

ROSS2 splits system responsibilities between two primary components: **The Server** and **The Swarm**.

                       +------------------------+
                       |   Authorized Users /   |
                       |   Remote Operators     |
                       +-----------+------------+
                                   |
                            (Secure Network)
                                   |
                       +-----------v------------+
                       |       THE SERVER       |
                       | (Tethered Base Station)|
                       +-----------+------------+
                                   |
                       (Wireless Swarm Mesh Network)
                                   |
        +--------------------------+--------------------------+
        |                          |                          |
    +--------v--------+        +--------v--------+        +--------v--------+
    |   Swarm Unit 1  | <----> |   Swarm Unit 2  | <----> |   Swarm Unit 3  |
    +-----------------+        +-----------------+        +-----------------+


### 1. The Server (Base Station & Deployment Hub)
The Server serves as the physical housing, launching platform, and network gateway for the robotic units:
* **Deployment Hub:** Houses 3 to 5 swarm units and deploys them on command.
* **Network Bridge:** Acts as the single point of entry between the low-level swarm network and external networks, allowing authorized operators to view telemetry and stream live video feeds.
* **Tethered Connection:** Utilizes a high-bandwidth tethered connection to maintain stable communications and power efficiency at the base station (tethering is planned to be wireless in future iterations).
* **Low-Cost Hardware Architecture:** Raspberry Pi 5 with an AI HAT for prototyping, but working on custom PCB to combine the two pieces and remove bloat.

### 2. The Swarm (Autonomous Observation Units)
The Swarm consists of 3 to 5 autonomous, mobile ground robots designed to systematically map and observe interior spaces:
* **Distributed Exploration:** Units automatically disperse in separate directions to maximize visual coverage of the environment (e.g., inside a burning building).
* **Inter-Robot Communication:** Swarm nodes communicate wirelessly with both neighboring units and the central server to coordinate movement, share state data, and route video streams back to the base station.
* **Low-Cost Hardware Architecture:** ESP32's for prototyping, will need to look into slightly higher performing boards in order to handle motor control, networking, and video.

---
