from flask import Flask, request, jsonify
from functools import wraps
import socket
import os
import logging
from dotenv import load_dotenv
from printers import printers
from zpl_generator import generate_zpl
from validation import validate_request

# Load environment variables
load_dotenv()
APIKEY = os.getenv('APIKEY')

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def require_apikey(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        apikey_received = request.headers.get('apikey')
        if not apikey:
            return jsonify({'error': 'API key is missing'}), 403
        if apikey_received != APIKEY:
            return jsonify({'error': 'Invalid API key', 'APIKEY': apikey_received}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/printers', methods=['GET'])
@require_apikey
def list_printers():
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
    status = {}
    for printer_id, printer_info in printers.items():
        online = check_printer_status(printer_info['ip'], printer_info['port'])
        status[printer_id] = 'Online' if online else 'Offline'
    return jsonify(status)

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
    errors = validate_request(request.json)
    if errors:
        return jsonify({'errors': errors}), 400

    data = request.json
    printer_id = data['printer_id']
    printer = printers.get(printer_id)
    if not printer:
        return jsonify({'error': 'Printer ID not found'}), 404

    zpl_command = generate_zpl(**data)
    try:
        send_zpl_to_printer(printer['ip'], printer['port'], zpl_command)
        return jsonify({'message': 'Label sent to printer successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host='0.0.0.0',
        port=int(os.getenv('FLASK_RUN_PORT', 5500))
    )