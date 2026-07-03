# Vision-Integrated Dual-Axis Solar Tracking System ☀️📸

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14+-FF6F00.svg)
![Arduino](https://img.shields.io/badge/Arduino-Hardware-00979D.svg)

An intelligent, edge-computing solar tracking system that utilizes Computer Vision and meteorological APIs to ensure strictly net-positive energy generation. By shifting from traditional "blind" continuous tracking to a dynamic cost-benefit algorithm, this system eliminates the mechanical energy wasted during overcast conditions.

### 🏛️ Academic Context
Developed at the **Department of Computer Science and Engineering (Data Science), Dwarkadas J. Sanghvi College of Engineering**.
* **Project Guide:** Dr. Kriti Shrivastava
* **Development Team:** Chinmay Chopade, Veer Dodiya, Hrishikesh Ganji, Nirjal Jagtap

---

## 📖 Table of Contents
1. [Problem Statement](#-problem-statement)
2. [System Architecture](#-system-architecture)
3. [The Mathematical Novelty](#-the-mathematical-novelty)
4. [Technology Stack](#-technology-stack)
5. [Project Structure](#-project-structure)
6. [Hardware Configuration](#-hardware-configuration)
7. [Getting Started](#-getting-started)

---

## 🎯 Problem Statement
Traditional dual-axis solar trackers rely on Light Dependent Resistors (LDRs) or fixed astronomical models. These act as "blind" systems that continuously expend motor energy to track the sun, even when it is completely obscured by heavy clouds. In diffused lighting, the kinetic energy consumed by the actuating motors frequently exceeds the marginal energy gained from adjusting the panel tilt, resulting in a net-negative energy yield. 

**Our Solution:** A vision-integrated cost-benefit algorithm that evaluates real-time cloud transmissivity and only permits motor actuation if the predicted solar energy gain strictly exceeds the electrical cost of mechanical movement.

---

## 🧠 System Architecture

The system is fully decoupled into three functional layers:

1. **The Perception Layer (Edge AI):** A ground-based sky imaging unit captures real-time fisheye images of the sky. A lightweight `MobileNetV2` Convolutional Neural Network (CNN)—trained on NREL Total Sky Imager (TSI) data—processes the image to output a continuous numerical prediction of the current Solar Irradiance ($W/m^2$).

2. **The Logic Layer (FastAPI Backend):** The central brain of the system. It wakes up on a strict 15-minute scheduled interval. It uses the `pvlib` library to calculate the sun's exact theoretical position and compares it against the panel's current angle. If the drift exceeds a $5^\circ$ threshold, it fetches the CNN's irradiance prediction, calculates expected power output, and runs the actuation inequality algorithm.

3. **The Hardware Layer (Actuation):** An Arduino microcontroller listening over a Serial connection. It translates the backend's verified coordinate commands into precise steps for the NEMA 17 stepper motors via A4988 drivers.

---

## 🧮 The Mathematical Novelty
This system transitions from *Gross Generation Tracking* to *Net-Positive Energy Optimization* using two deterministic equations:

**1. Hardware-Aware Expected Generation:**
Instead of relying on secondary black-box ML models, the system predicts exact power yield using established photovoltaic physics:
$$E_{\text{gain}} = A \times r \times H \times PR$$
*(Where $A$ = Panel Area, $r$ = Panel Efficiency, $H$ = CNN Predicted Irradiance, $PR$ = Performance Ratio)*

**2. The Actuation Gatekeeper Inequality:**
The backend completely prohibits physical motor movement unless the following condition is met:
$$E_{\text{gain}} - E_{\text{current\_position}} > E_{\text{motor}} + E_{\text{safety\_margin}}$$
This guarantees that the system never burns battery power to chase negligible solar gains.

---

## 💻 Technology Stack

**Machine Learning & Vision**
* `TensorFlow` / `Keras` (MobileNetV2 for Transfer Learning)
* `OpenCV` (Image processing)
* `Pandas` & `NumPy` (Data engineering and timestamp merging)

**Backend & Logic**
* `FastAPI` (REST API & routing)
* `Uvicorn` (ASGI Server)
* `pvlib-python` (Astronomical clear-sky baselines)
* `APScheduler` (15-minute background asynchronous loops)

**Data Sources & APIs**
* **NREL NSRDB API:** Live baseline meteorological data (GHI, DNI, Wind Speed).
* **NREL TSI / SWIMCAT:** Training datasets for the CNN regression model.
* **Kaggle Solar Generation Data:** Historical validation for expected energy outputs.

---

## 📁 Project Structure

```text
vision-solar-tracker/
│
├── main.py                     # Entry point: Starts FastAPI and APScheduler
├── models/
│   └── irradiance_cnn.h5       # Trained MobileNetV2 regression weights
│
├── routers/
│   └── tracker_routes.py       # API Endpoints (e.g., /force-check, /status)
│
├── services/
│   ├── prediction.py           # ML inference: Image -> W/m^2
│   ├── calculator.py           # pvlib math, 5° angle checks, and inequality logic
│   └── hardware_serial.py      # Pyserial communication with Arduino
│
├── schemas/
│   └── api_models.py           # Pydantic data validation schemas
│
├── arduino_firmware/
│   └── stepper_control.ino     # C++ code for Arduino Uno & A4988 drivers
│
├── requirements.txt
└── README.md
