# Quanser 2-DOF Helicopter - Tuning & Simulation Platform

This repository contains a full-stack platform for the simulation, control, and multi-objective optimization (tuning) of a Quanser 2-DOF (Degree of Freedom) Helicopter system. It features an interactive web interface for running tuning algorithms, tracking historical data, and analyzing performance using an advanced backend built with FastAPI and Python.

## System Architecture

* **Frontend**: React (Vite), ReactECharts, Lucide React, Axios.
* **Backend**: Python, FastAPI, NumPy, Control, PySwarms, SciPy, Motor (Async MongoDB).
* **Database**: MongoDB Atlas.

## Key Features

* **Physics Simulation**: Custom continuous-time simulation environment for the 2-DOF Helicopter.
* **Control Strategies**:
  * Classic Decentralized PID.
  * Model-based Gravity Compensation.
  * Fuzzy Logic PID (Gain Scheduling).
* **Optimization Algorithms**:
  * Particle Swarm Optimization (PSO).
  * Genetic Algorithm (GA).
  * Bayesian Optimization (BO).
* **Multi-Objective Cost Function**: Custom ITAE, Energy, Smoothness, and Saturation penalties, scaled dynamically based on simulation duration.
* **Historical Tuning Dashboard**: Automatically saves all tuning results to MongoDB Atlas and visualizes historical progress and parameter sweeps.

## Installation

### 1. Prerequisites
* Python 3.10+
* Node.js v16+
* MongoDB Atlas Cluster (or local instance)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # (Windows)
# source venv/bin/activate # (Mac/Linux)
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory by copying the `.env.example`:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<AppName>
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

You can use the provided `start_project.bat` (on Windows) to launch both servers simultaneously:
```bash
./start_project.bat
```

Or manually:
* **Backend**: `cd backend && uvicorn main:app --port 8088 --reload`
* **Frontend**: `cd frontend && npm run dev`

Navigate to `http://localhost:5173` in your browser.

## Documentation
For in-depth mathematical documentation on the objective functions, normalization, and optimization techniques, refer to the **Documentation** tab in the web interface.

## License
MIT License
