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
    'prt-batch-TWR2': {'ip': '10.1.0.49', 'port': 9100},
    'prt-batch-WE1': {'ip': '10.1.0.25', 'port': 9100},
    'prt-batch-WE2': {'ip': '10.1.0.26', 'port': 9100},
    'prt-batch-WE3': {'ip': '10.1.0.27', 'port': 9100},
    'prt-batch-WE4': {'ip': '10.1.0.28', 'port': 9100},
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


def generate_zpl(batch, item_code, description_line1, description_line2, manufacturer, manufacturer_part, warehouse, parent_warehouse, msl, qty, date, user):
    """
    Generates ZPL command string for a simple label with the given text.
    """
    return f"""
        ^XA

    ^FO280,10
    ^BQN,2,6,H
    ^FDMM,A{batch}^FS

    ^CF0,20
    ^FO20,20^FDBatch^FS
    ^CF0,70
    ^FO20,45^FD{batch}^FS

    ^CF0,20
    ^FO20,115^FDItem Code^FS
    ^CF0,40
    ^FO20,140^FD{item_code}^FS

    ^CF0,20
    ^FO20,190^FDDescription^FS
    ^CF0,20
    ^FO20,215^FD{description_line1}^FS
    ^FO20,235^FD{description_line2}^FS

    ^CF0,20
    ^FO20,270^FDManufacturer^FS
    ^CF0,30
    ^FO20,295^FD{manufacturer}^FS
    ^CF0,30
    ^FO20,325^FD{manufacturer_part}^FS

    ^CF0,20
    ^FO280,180^FDIncoming^FS
    ^CF0,40
    ^FO280,205^FD{warehouse}^FS
    ^CF0,30
    ^FO280,245^FD{parent_warehouse}^FS

    ^CF0,40
    ^FO280,285^GB130,68,5,B,0^FS
    ^FO295,305^FDMSL{msl}^FS

    ^CF0,20
    ^FO20,370^FDQty^FS
    ^CF0,20
    ^FO20,395^FD{qty}^FS

    ^CF0,20
    ^FO90,370^FDDate^FS
    ^CF0,20
    ^FO90,395^FD{date}^FS

    ^CF0,20
    ^FO210,370^FDUser^FS
    ^CF0,20
    ^FO210,395^FD{user}^FS

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
    if not printer_id:
        return jsonify({'error': 'Missing printer_id'}), 400
    
    batch = data.get('batch')
    if not batch:
        return jsonify({'error': 'Missing batch'}), 400
    
    item_code = data.get('item_code')
    if not item_code:
        return jsonify({'error': 'Missing item_code'}), 400
    
    description_line1 = data.get('description_line1')
    if not description_line1:
        return jsonify({'error': 'Missing description_line1'}), 400
    
    description_line2 = data.get('description_line2')
    if not description_line2:
        return jsonify({'error': 'Missing description_line2'}), 400
    
    manufacturer = data.get('manufacturer')
    if not manufacturer:
        return jsonify({'error': 'Missing manufacturer'}), 400
    
    manufacturer_part = data.get('manufacturer_part')
    if not manufacturer_part:
        return jsonify({'error': 'Missing manufacturer_part'}), 400
    
    warehouse = data.get('warehouse')
    if not warehouse:
        return jsonify({'error': 'Missing warehouse'}), 400
    
    parent_warehouse = data.get('parent_warehouse')
    if not parent_warehouse:
        return jsonify({'error': 'Missing parent_warehouse'}), 400
    
    msl = data.get('msl')
    if not msl:
        return jsonify({'error': 'Missing msl'}), 400
    
    qty = data.get('qty')
    if not qty:
        return jsonify({'error': 'Missing qty'}), 400

    date = data.get('date')
    if not date:
        return jsonify({'error': 'Missing date'}), 400
    
    user = data.get('user')
    if not user:
        return jsonify({'error': 'Missing user'}), 400

    

    printer = printers.get(printer_id)
    if not printer:
        return jsonify({'error': 'Printer ID not found'}), 404

    zpl_command = generate_zpl(batch, item_code, description_line1, description_line2, manufacturer, manufacturer_part, warehouse, parent_warehouse, msl, qty, date, user)
    try:
        send_zpl_to_printer(printer['ip'], printer['port'], zpl_command)
        return jsonify({'message': 'Label sent to printer successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
