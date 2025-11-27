# Wind Turbine Gearbox Analytics Builder Demo

This repository contains a complete end-to-end demo pipeline for Cumulocity Analytics Builder that showcases how MQTT ingestion, JavaScript preprocessing, ONNX inference, rule-based postprocessing, and LLM-driven diagnostics work together to detect and respond to emerging gearbox faults in a wind turbine.

The project is intentionally lightweight but representative of how a real industrial monitoring workflow can be implemented.

## Overview

The demo simulates a wind turbine gearbox producing vibration, temperature, and torque data over MQTT. Analytics Builder ingests this data, transforms it, runs it through an ONNX model, applies rule-based logic, and escalates faults via an LLM agent.

Pipeline steps:

1. MQTT Data Source
   A Python script publishes Base64-encoded binary payloads containing:
   * 8 vibration FFT bins
   * gearbox temperature
   * gearbox torque
   The script injects occasional synthetic failure conditions (bearing wear, gear tooth damage, shaft misalignment).

2. JavaScript Preprocessing Function
   The first Analytics Builder JavaScript block:
   * receives Base64 binary MQTT payload
   * decodes it into 10 float values
   * extracts temperature and torque
   * forwards the feature vector to the ONNX model
   * forwards additional values directly to the second JS function

3. ONNX Inference Model
   A small feed-forward neural network classifies the input into one of four states:
   * 0 normal
   * 1 early_bearing_wear
   * 2 gear_tooth_damage
   * 3 misalignment
   The model outputs a class ID and confidence score.

4. JavaScript Decision Function
   The second JS block receives:
   * raw features
   * temperature and torque
   * ONNX classification and confidence
   It produces either:
   * a normal measurement payload for healthy cases, or
   * a structured LLM prompt for fault cases

5. LLM Diagnostic Agent
   When a fault is detected, the LLM receives the classification, confidence, and raw features and produces:
   * root cause analysis
   * secondary effects
   * recommended engineering checks
   A system prompt template is provided to keep responses consistent.

## Repository Contents

* data_generator.py – publishes simulated gearbox data over MQTT
* model_trainer.py – trains a small model and exports gearbox_model.onnx
* decoding.js – preprocessing Smart Function
* decision.js – decision/LLM-trigger Smart Function
* agent-system-prompt.txt – system prompt for the diagnostic agent
* model-readable.json - a readable version of the Analytics Builder Model JSON

## How to Run the Demo

### 1. Train or regenerate the ONNX model (optional)

Run:
`python3 model_trainer.py`

This produces gearbox_model.onnx.

### 2. Simulate gearbox data over MQTT

Set MQTT broker details in data_generator.py. Then run:
`python3 data_generator.py`

This publishes one message per second for 10 minutes, including rare injected failures.

### 3. Configure Analytics Builder

1. Add the MQTT source subscribed to the simulator’s topic.
2. Add a JavaScript block with decoding.js.
3. Add the ONNX inference block with gearbox_model.onnx.
4. Add a JavaScript block with decision.js.
5. Wire the blocks so that:
   * JS1 → ONNX (feature vector)
   * JS1 → JS2 (temperature, torque, etc.)
   * ONNX → JS2 (class and confidence)
6. Connect JS2 outputs to Measurements (healthy) and the LLM Agent (faults).

### 4. Configure the LLM Agent

Use agent-system-prompt.txt as the system prompt for consistent, professional responses.

## Expected Demo Behaviour

During the 10-minute run:
• Most samples classify as normal.
• A few are labelled as early bearing wear, gear tooth damage, or misalignment.
Healthy cases generate standard Cumulocity measurements.
Fault cases produce a structured diagnostic from the LLM, which can be routed to alarms, notifications, or downstream workflows.

## Customisation

Possible extensions:
* more failure types
* a richer vibration spectrum
* additional turbine metadata
* multi-turbine simulation
* larger or recurrent ML models

## Purpose

This demo provides a realistic industrial analytics pipeline suitable for:
* customer workshops
* solution architecture demos
* training sessions
* internal capability showcases

It remains easy to deploy while mirroring an actual predictive maintenance workflow for wind turbine drivetrain components.

