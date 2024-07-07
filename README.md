# Sensing and IoT Project
This project involves the collection and actuation of data using various IoT sensors. It leverages Python scripts for data collection, actuation, and overall application management. The project is designed to use Google Cloud services for data storage and management.

# Project Structure
**actuations.py**: This script handles the actuation logic for the IoT devices. <br />
**app.py**: The main application script that integrates all components and runs the application.<br />
**data_collection.py**: Script responsible for collecting data from the IoT sensors.<br />
**sensing-and-iot-project-697ae27b6369.json**: Service account key file for accessing Google Cloud services.<br />

# Required Python Packages
Install the required Python packages using the following command: <br />
pip install -r requirements.txt<br />

# Google Cloud Setup
One will need to set up their own Google Cloud API and plug that into the project to run it.

# Running the application
Data Collection:<br />
python data_collection.py <br />
<br />
Actuation:<br />
python actuations.py<br />
<br />
Main Application:<br />
python app.py<br />
<br />
# Usage
**Data Collection**: The data_collection.py script will continuously collect data from connected IoT sensors and send it to the designated storage. <br />
**Actuation**: The actuations.py script will listen for actuation commands and control the IoT devices accordingly. <br />
**Application Interface**: The app.py script provides a user interface to manage and monitor the IoT system.<br />
