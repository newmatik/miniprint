# MiniPrint - Zebra Printer API Server

This Flask application provides a REST API to interact with Zebra label printers on a network. It supports listing all registered printers, checking their online status, and sending ZPL commands to print labels directly from supplied text.

## Features

- **List Printers**: Retrieve a list of all configured printers with their IP addresses and ports.
- **Check Printer Status**: Check the online/offline status of each printer.
- **Print Labels**: Send text to a printer to be printed on a label using Zebra Programming Language (ZPL).

## Setup

### Prerequisites

- Python 3.6 or higher
- Flask

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/newmatik/miniprint.git
   cd miniprint
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install flask
   ```
   
Set the API key and printer details in the script. Replace 'your_api_key_here' with your actual API key and update the printers dictionary with your printer configurations.

4. Running the Server
   
Run the server with the following command:
  ```bash
  python app.py
  ```

This starts the server on http://0.0.0.0:5500/, making it accessible on all network interfaces on port 5500.

## Usage

### GET /printers

Requires API key
Returns a list of all printers

### GET /printers/status

Requires API key
Returns the status of each printer

### POST /print

Requires API key
JSON payload: {"printer_id": "prt-batch-TWR1", "text": "Sample Text"}
Sends the specified text to the printer to be printed

Example Request

Using curl to check printer status:

```bash
curl -X GET http://localhost:5500/printers/status -H "apikey: g9d8fh09df8hg09f8siw3erfsd8"
```

## Deployment on Ubuntu Server

To ensure that the Flask application starts automatically at server boot and restarts in case it crashes, we use systemd on Ubuntu.

### Create a Service File

First, create a systemd service file for your Flask application. You’ll need root or sudo privileges to write to the service directory.

Open a terminal and use your preferred text editor to create a service file:

```
sudo nano /etc/systemd/system/miniprint.service
```

Add the following configuration to the file, customizing it to suit your application setup:

```
[Unit]
Description=Flask Application Service
After=network.target

[Service]
User=your_username
Group=your_usergroup
WorkingDirectory=/path/to/your/application
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Enable and Start the Service

After saving your service file, you'll need to reload the systemd manager configuration, enable the service to start on boot, and then start the service:

```
sudo systemctl daemon-reload
sudo systemctl enable miniprint.service
sudo systemctl start miniprint.service
```

### Check the Status of Your Service

To check the status of your service and ensure it's running properly:

```
sudo systemctl status miniprint.service
```

## Security
The API uses a hardcoded API key for authentication. It is recommended to use a more secure API key management system for production environments.

## Logging
Logging is set to DEBUG level, capturing detailed logs that can assist in diagnosing issues or understanding application behavior.

## Note
This application is designed for demonstration and development purposes and may require additional security and error handling features for production use.
