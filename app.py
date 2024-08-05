from flask import Flask, request, jsonify
from flask_restful import Api, Resource
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
api = Api(app)
logging.basicConfig(level=logging.DEBUG)

def require_apikey(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        apikey_received = request.headers.get('apikey')
        if not apikey_received:
            return {'error': 'API key is missing'}, 403
        if apikey_received != APIKEY:
            return {'error': 'Invalid API key'}, 403
        return f(*args, **kwargs)
    return decorated_function

class PrinterList(Resource):
    method_decorators = [require_apikey]

    def get(self):
        logging.debug(request.headers)
        return printers

class PrinterStatus(Resource):
    method_decorators = [require_apikey]

    def get(self):
        status = {}
        for printer_id, printer_info in printers.items():
            online = self.check_printer_status(printer_info['ip'], printer_info['port'])
            status[printer_id] = 'Online' if online else 'Offline'
        return status

    def check_printer_status(self, printer_ip, printer_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)  # Set timeout to 5 seconds
            try:
                sock.connect((printer_ip, printer_port))
                return True
            except socket.error as e:
                print(f"Failed to connect to {printer_ip}:{printer_port} - {e}")
                return False

class PrintLabel(Resource):
    method_decorators = [require_apikey]

    def post(self):
        errors = validate_request(request.json)
        if errors:
            return {'errors': errors}, 400

        data = request.json
        printer_id = data['printer_id']
        printer = printers.get(printer_id)
        if not printer:
            return {'error': 'Printer ID not found'}, 404

        zpl_command = generate_zpl(**data)
        try:
            self.send_zpl_to_printer(printer['ip'], printer['port'], zpl_command)
            return {'message': 'Label sent to printer successfully'}
        except Exception as e:
            return {'error': str(e)}, 500

    def send_zpl_to_printer(self, printer_ip, printer_port, zpl_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((printer_ip, printer_port))
            sock.sendall(zpl_data.encode('utf-8'))

class PrintMSLLabel(Resource):
    method_decorators = [require_apikey]

    def post(self):
        errors = validate_request(request.json)
        if errors:
            return {'errors': errors}, 400

        data = request.json
        printer_id = data['printer_id']
        printer = printers.get(printer_id)
        if not printer:
            return {'error': 'Printer ID not found'}, 404

        zpl_command = generate_msl_sticker(**data)
        try:
            self.send_zpl_to_printer(printer['ip'], printer['port'], zpl_command)
            return {'message': 'Label sent to printer successfully'}
        except Exception as e:
            return {'error': str(e)}, 500

    def send_zpl_to_printer(self, printer_ip, printer_port, zpl_data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((printer_ip, printer_port))
            sock.sendall(zpl_data.encode('utf-8'))

class HelloWorld(Resource):
    def get(self):
        return {'message': 'miniprint api'}
    
class Ping(Resource):
    def get(self):
        return {'message': 'pong'}

# Add resources
api.add_resource(HelloWorld, '/')
api.add_resource(Ping, '/ping')
api.add_resource(PrinterList, '/printers')
api.add_resource(PrinterStatus, '/printers/status')
api.add_resource(PrintLabel, '/print')
api.add_resource(PrintMSLLabel, '/print/msl')

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host='0.0.0.0',
        port=int(os.getenv('FLASK_RUN_PORT', 5500))
    )
