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
   pip install -r requirements.txt
   ```

4. Environment setup:
   Copy .env_sampe to .env and set the API key. Update the printers dictionary with your printer configurations in printers.py.
   ```bash
   cp .env_sample .env
   vim .env
   ```

5. Running the Server:
   Run the server with the following command:
   ```bash
   flask run
   ```
   This starts the server on http://0.0.0.0:5500/, making it accessible on all network interfaces on port 5500.

## Usage

- **GET /printers**
   Requires API key
   Returns a list of all printers

- **GET /printers/status**
   Requires API key
   Returns the status of each printer (online, offline)

- **POST /print**
   Requires API key
   Prints the ZPL label to the specified printer

### Example Request

Using curl to check printer status:

```bash
curl -X GET http://localhost:5500/printers/status -H "apikey: g9d8fh09df8hg09f8siw3erfsd8"
```

## Deployment on Ubuntu Server

To ensure that the Flask application starts automatically at server boot and restarts in case it crashes, we use systemd on Ubuntu.
Consider deploying with a production-ready WSGI server like Gunicorn.

### Create a Service File

First, create a systemd service file for your Flask application. You’ll need root or sudo privileges to write to the service directory.

Open a terminal and use your preferred text editor to create a service file:

```bash
sudo nano /etc/systemd/system/miniprint.service
```

Add the following configuration to the file, customizing it to suit your application setup:

```bash
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

```bash
sudo systemctl daemon-reload
sudo systemctl enable miniprint.service
sudo systemctl start miniprint.service
```

### Check the Status of Your Service

To check the status of your service and ensure it's running properly:

```bash
sudo systemctl status miniprint.service
```

## Note
This application is designed for demonstration and development purposes and may require additional security and error handling features for production use.
