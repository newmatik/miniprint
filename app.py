from flask import Flask, request, jsonify
from functools import wraps
import socket
import logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to ensure all debug logs are captured

# Hardcoded API key, replace 'your_api_key_here' with your actual API key
APIKEY = 'g9d8fh09df8hg09f8siw3erfsd8'

app = Flask(__name__)

# This dictionary should contain the IP and port of each printer by ID
printers = {
    'prt-batch-TWR1': {'ip': '10.1.0.48', 'port': 9100},
    # Add more printers as needed
}

def require_apikey(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'apikey' not in request.headers:
            return jsonify({'error': 'apikey is missing'}), 403

        # Direct comparison of the API key provided in the request with the hardcoded one
        if request.headers['apikey'] != APIKEY:
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/printers', methods=['GET'])
@require_apikey
def list_printers():
    """
    Returns a list of all registered printers with their details.
    """
    # Log headers for debugging
    logging.debug(request.headers)
    return jsonify(printers)

def check_printer_status(printer_ip, printer_port):
    """
    Checks if the printer is online by attempting to open a TCP connection.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)  # Set timeout to 5 seconds
        try:
            sock.connect((printer_ip, printer_port))
            return True
        except socket.error as e:
            print(f"Failed to connect to {printer_ip}:{printer_port} - {e}")
            return False

@app.route('/printers/status', methods=['GET'])
@require_apikey
def printers_status():
    """
    Returns the status of all registered printers, indicating if they are online or offline.
    """
    status = {}
    for printer_id, printer_info in printers.items():
        online = check_printer_status(printer_info['ip'], printer_info['port'])
        status[printer_id] = 'Online' if online else 'Offline'
    return jsonify(status)


def generate_zpl(label_text):
    """
    Generates ZPL command string for a simple label with the given text.
    """
    return f"""
    ^XA
    ^CF0,60
    ^FO50,50^FD{label_text}^FS
    ^XZ
    """

def send_zpl_to_printer(printer_ip, printer_port, zpl_data):
    """
    Sends ZPL command to the specified printer.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((printer_ip, printer_port))
        sock.sendall(zpl_data.encode('utf-8'))

@app.route('/print', methods=['POST'])
@require_apikey
def print_label():
    data = request.json
    printer_id = data.get('printer_id')
    text = data.get('text')

    if not printer_id or not text:
        return jsonify({'error': 'Missing printer_id or text'}), 400

    printer = printers.get(printer_id)
    if not printer:
        return jsonify({'error': 'Printer ID not found'}), 404

    zpl_command = generate_zpl(text)
    try:
        send_zpl_to_printer(printer['ip'], printer['port'], zpl_command)
        return jsonify({'message': 'Label sent to printer successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
