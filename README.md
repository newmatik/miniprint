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

### Creating a systemd Service

1. **Create a systemd service file**:
   - Location: `/etc/systemd/system/miniprint.service`
   - Ensure you customize the service file with the correct paths and user information.

2. **Enable the Service**:
   - Run `sudo systemctl enable miniprint.service` to enable automatic startup at boot.

3. **Start the Service**:
   - Run `sudo systemctl start miniprint.service` to start the service immediately.

4. **Service Management Commands**:
   - **Check status**: `sudo systemctl status miniprint.service`
   - **Restart service**: `sudo systemctl restart miniprint.service`
   - **Stop service**: `sudo systemctl stop miniprint.service`

This setup ensures that your application is resilient to crashes and is always available after system reboots.

## Security
The API uses a hardcoded API key for authentication. It is recommended to use a more secure API key management system for production environments.

## Logging
Logging is set to DEBUG level, capturing detailed logs that can assist in diagnosing issues or understanding application behavior.

## Note
This application is designed for demonstration and development purposes and may require additional security and error handling features for production use.
