# **5G Remote Driving Robot**

<img src="https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/8ede59d5-f162-4ff3-a3eb-c810e3935596" width=50% height=50%>

## **Introduction**

The main goal of this project is to develop a vehicle which can autonomously move having basic obstacle avoidance behavior, and which at the same time exposes monitoring and command & control capabilities over 5G networks. The solution is built around a Raspberry Pi which stands within a COTS vehicle platform equipped with servo motors controlling a set of two wheel axes. The Raspberry Pi has a connected 5G hat, configurable for the registration of the vehicle in private and public 5G networks. A Python script, developed and deployed on the RPI provides a runtime environment capable of interface with the on-board GPIO, integrating low-level oriented libraries, and provides servo motors control and other sensor integration, e.g. sonar sensor. Briefly the runtime script exposes an API to receive navigation commands by external agents or operators and also publishes metrics and data, as collected from the on-boarded sensors to an MQTT broker.

The MQTT broker is deployed in a separate machine along with an InfluxDB and an agent which subscribes to the broker and automatically pushes all metrics to the time-series database. A visualization dashboard is built to source data from the TSDB and produce comprehensive visualizations. Additionally a script which can pull and process data, based on smart and AI algorithms, from the TSDB can publish event payloads back to the broker or directly call Raspberry exposed API to perform navigation adaptations.

All components, both in RPI and external machine are packaged as containerized format and are orchestrated by Kubernetes orchestrator. The chosen Kubernetes flavor for our current deployment is k3s as a light weight solution which can be efficiently supported on different RPI models with heterogeneous capabilities.

## **Requirements**

### **Hardware:**

- Robot Chassis
- Raspberry Pi 4(preferred)
- 4 DC motors
- L298N Dual H Bridge (DC motor driver)
- Jumper wires
- 4 wheels
- 1 Ultrasonic sensor module (preferred HC-SR04)
- 5G hat
- 6 batteries x 1.5V each (9V in total)

### **Software:**

#### **Raspberry Pi**

- Operating system Raspbian GNU/Linux 10 (buster)
- Python version 3.7 or higher
- FastApi python library ([https://fastapi.tiangolo.com](https://fastapi.tiangolo.com/))
- GPIO python library ([https://pypi.org/project/RPi.GPIO](https://pypi.org/project/RPi.GPIO))
- Paho-mqtt python library ([https://pypi.org/project/paho-mqtt](https://pypi.org/project/paho-mqtt))
- Docker
- K3s-lightweight kubernetes
- Nginx

####


#### **Host Machine**

- VM with Ubuntu 22.04.2 LTS (jammy)
- MQTT mosquitto broker
- InfluxDB + telegraf agent
- Docker
- K3s-lightweight kubernetes

## **System Architecture**
![Pi_robot (4)](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/c207a9da-9026-44f7-acf1-9dd5e957322c)

The Kubernetes cluster consists of two nodes: the master node, which runs on the host/virtual machine, and the worker node, which runs on the Raspberry Pi board. Every pod running on each node uses containerd as the default Container Runtime Interface (CRI) in k3s. Pods can communicate with each other within a Kubernetes cluster, each pod is assigned a unique IP address (with the help of services) within the cluster's network. Pods can communicate with each other directly using these IP addresses. Overall that's how the containerized applications can "speak" to each other inside the cluster.

## **Implementation**

### Raspberry Pi

To formally articulate the process of implementing FastAPI, Nginx, and mqtt.client script applications within a Kubernetes cluster, it is imperative to construct corresponding Docker images with the proper configurations designed for the k3s worker node. Initially, this procedure necessitates the generation of a FastAPI script that harnesses the robot movement endpoints. Subsequently, one must establish the Nginx configuration to proficiently manage incoming requests. In the final stage, it is required to generate an mqtt.client script using the Paho library, a script that publishes sonar reading data in real time to the Mosquitto broker, which is situated on the host machine. Through the execution of these steps, the configuration and setup workflow for the k3s worker node in the Kubernetes cluster can be successfully concluded.

### Host Machine

The process for building Docker images for the k3s master node is consistent across the Mosquitto broker, Telegraf, and InfluxDB applications. The Mosquitto broker collects all data from the mqtt.client script. Then, with the help of the Telegraf agent, this data is sent to InfluxDB, allowing for monitoring and storage of the sonar sensor's data in the database. After these Docker images are created with the necessary configurations, the next step is to create the corresponding Kubernetes manifest files (deployments-services) for each application using the created images.

In the manifest file for each application, we designate the specific node where the application should run. For instance, we specify that the FastAPI, Nginx, and mqtt.client applications should operate on the k3s worker node. Contrariwise, the Mosquitto broker, Telegraf, and InfluxDB are set to run on the host machine.

The two applications that need to be accessed are FastAPI and InfluxDB. FastAPI provides robotic control capabilities, while InfluxDB facilitates data monitoring processes. Access to these services can be established through the service IPs, generated via Kubernetes manifest services. Those IPs are exclusively visible within the cluster. For these services to be accessible beyond the cluster, an ingress controller is required. This allows services to be exposed to the wider local network, enabling all users within the same network to gain access to both FastAPI and InfluxDB. By default, the k3s system uses Traefik as the ingress controller. Leveraging this controller, a manifest file can be created to instruct the system to expose FastAPI and InfluxDB beyond the confines of the cluster. In conclusion, upon application of all the manifest files within the Kubernetes cluster, the services can be accessed through the URLs: `influxdb.test` and `nginx.test/docs`.(update the local host in the /etc/hosts of your machine).

## **Example/Screenshots**
 **Local Machine:**

Checking the state of k3s-master/worker-node: `kubectl get nodes -o wide`
![Screenshot 2023-07-24 140121](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/02616e69-3864-4e96-9089-4242a53d3157)
Deploying minifest files on both nodes: `kubectl apply -f .`
![Screenshot 2023-07-24 140051](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/a188d641-3cff-4202-bfd8-de7c0d3826a6)

Checking pods/services/deployments are correctly running in the kubernetes cluster: `kubectl get all`
![Screenshot 2023-07-24 140156](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/30a13401-f7b0-431a-8d2f-488343780ca1)
The pods are running on the nodes that are being designated in the manifest files:`kubectl get pods -o wide`
![Screenshot 2023-07-24 141522](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/adbf91ab-55aa-4511-b9f3-3bf72a4bd838)
Access influxdb database for monitoring and storing sensor data in real-time:
![Screenshot 2023-07-24 140933](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/223a6370-ea5d-4a90-876d-d4ee6d792f68)
Control the robot using FastApi endpoints:
![Screenshot 2023-07-24 141005](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/68bfd365-b27b-460f-9f76-78f2dff6eac8)
**Raspberry Pi:**

The structure of the k3s-worker-node files should look like this:



![Screenshot 2023-07-24 143322](https://github.com/FRONT-research-group/5G-Driving-robot/assets/94470659/928f7290-7c57-4c94-8824-b1e38dd2358c)



## **Commands**

- To deploy, go to k3s-master-node folder and run : `kubectl apply -f .`
- To delete the manifests deployment: `kubectl delete all - - all`

## **Issues**

- Change the IP addresses and kubernetes service names located in the files with the corresponding ones of your system
- Sometimes mqtt client pod needs restart
