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

2. DataPreparation JavaScript Smart Function
	* Data Preparation rule receives from the MQTT source
	* Decodes the binary payload
	* Creates a Cumulocity Event with the decoded raw values for inference

3. JavaScript Preprocessing Function
   The first Analytics Builder JavaScript block:
	* Extracs from the Cumulocity Event the feature vector and temp/torque values
   * forwards the feature vector to the ONNX model
   * forwards additional values directly to the second JS function

4. ONNX Inference Model
   A small feed-forward neural network classifies the input into one of four states:
   * 0 normal
   * 1 early_bearing_wear
   * 2 gear_tooth_damage
   * 3 misalignment
   The model outputs a class ID and confidence score.

5. JavaScript Decision Function
   The second JS block receives:
   * temperature and torque
   * ONNX classification and confidence
   It produces either:
   * a normal measurement payload for healthy cases, or
   * a structured LLM prompt for fault cases

7. LLM Diagnostic Agent
   When a fault is detected, the LLM receives the classification, confidence, and raw features and produces:
   * root cause analysis
   * secondary effects
   * recommended engineering checks
   A system prompt template is provided to keep responses consistent.

8. Alarm and Measurement creation
	On non-faults, measurements are created for temperature and torque.
	On faults alarms are raised with the RCA and recommended checks

## Repository Contents

* data_generator.py – publishes simulated gearbox data over MQTT
* model_trainer.py – trains a small model and exports gearbox_model.onnx
* data_prep_decoding.js - data decoding Smart Function
* preprocessing.js – preprocessing Smart Function
* decision.js – decision/LLM-trigger Smart Function
* agent-system-prompt.txt – system prompt for the diagnostic agent
* AI Vision.json - Analytics model
* gearbox_model.onnx - Trained ONNX model
* requirements.txt - Python dependencies for training and simulation

## How to Run the Demo

You will need a tenant with at least Apama version v27.50.0 deployed, and subscribed to:

* data-prep-ctrl
* Data Preparation
* Data Prep Plugin
* AI agents (0.8.5+)
* AI plugin (0.8.5+)

### Train or regenerate the ONNX model (optional)

Run:
`python3 model_trainer.py`

This produces gearbox_model.onnx.

### Upload the ONNX model

Zip gearbox_model.onnx and gearbox_model.onnx.data into gearbox_model.zip
Upload the zip to the files repository in the Administration page

### Configure the LLM Agent

Create an AI Agent in the AI Agent Manager using agent-system-prompt.txt

### Create the Data Preparation rule

Create a Data Preparation rule subscribed to MQTT topic turbine/gearbox/data

Use data_prep_decoding.js as the Smart Function, or get the AI to generate it with the prompt:

	The payload is binary packed 10 32-bit floats in big endian. The last two are the temperature and torque, the rest are raw features. Create a Cumulocity Event with type ai_InferenceInput containing fragments temperature.value, torque.value and rawValues.values

### Create the Analytics Builder model

Upload AI Vision.json as an Analytics Builder Model, or create your own model with:

* Event input block
	- source: Template Device (From Context)
	- event type: ai_InferenceInput
	- New events only
* Smart Function block 1
	- inputs[0] from Event output
	- Smart Function from preprocessing.js
* ONNX block
	- Input from SF1 outputs[2]
	- Model name: Template Inference Model Name
* Smart Function block 2
	- inputs[0] from SF1 outputs[0]
	- inputs[1] from SF1 outputs[1]
	- inputs[2] from ONNX output
	- Smart Function from decision.js
* Measurement output block
	- destination: Template Device
	- fragment name: c8y_Temperature
	- series name: c8y_Temperature
	- Value input from SF2 outputs[0]
	- Send input from SF2 outputs[2]
* Measurement output block
	- destination: Template Device
	- fragment name: c8y_Torque
	- series name: c8y_Torque
	- Value input from SF2 outputs[1]
	- Send input from SF2 outputs[2]
* Rate Limiter block
	- Input from SF2 outputs[3]
	- Period 60
* AI agent block
	- inputs[0] from Rate Limiter output
	- Agent name: Template Analysis Agent Name
	- template: {{inputs[0]}}
* Alarm output block
	- destination: Template Device
	- Alarm type: ai_gearBearingIssue
	- Severity Major
	- Create input from AI agent output
	- Message input from AI agent output

### Simulate gearbox data over MQTT

Set MQTT broker details in data_generator.py. Then run:
`python3 data_generator.py`

This publishes one message per second for 10 minutes, including rare injected failures.

Data Preparation will then automatically create the device and start posting Events to it


### Enable analytics on the device

Go to Smart Rules (new) tab on the device, and create a new instance of your AB model with:

* Inference Model Name: gearbox_model
* Analysis Agent Name: the name of the agent you created

## Expected Demo Behaviour

In the device Measurements tab you should see:

* The Event created by data prep
* The Temperature measurements
* The Torque measuremnts

In the Alarms tab you should see the created alarm.
