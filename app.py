from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from functools import wraps
import socket
import os
import logging
from dotenv import load_dotenv
from printers import printers
from zpl_generator import generate_zpl, generate_msl_sticker, generate_special_instructions_label, generate_dry_label, generate_tracescan_label
from validation import validate_request, validate_msl_request, validate_special_instructions_request, validate_dry_request, validate_tracescan_request

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

# Common printer communication mixin
class PrinterCommunicationMixin:
    def send_zpl_to_printer(self, printer_ip, printer_port, zpl_data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)  # Add timeout for better error handling
                sock.connect((printer_ip, printer_port))
                sock.sendall(zpl_data.encode('utf-8'))
        except socket.timeout as e:
            logging.error(f"Connection timeout to printer at {printer_ip}:{printer_port}")
            raise Exception("Printer connection timeout") from e
        except socket.error as e:
            logging.error(f"Socket error while connecting to printer at {printer_ip}:{printer_port}: {str(e)}")
            raise Exception(f"Printer connection error: {str(e)}") from e
        except Exception as e:
            logging.error(f"Unexpected error while sending data to printer: {str(e)}")
            raise

    def get_printer_info(self, printer_id):
        printer = printers.get(printer_id)
        if not printer:
            raise ValueError('Printer ID not found')
        return printer

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
            try:
                online = self.check_printer_status(printer_info['ip'], printer_info['port'])
                status[printer_id] = 'Online' if online else 'Offline'
            except Exception as e:
                logging.error(f"Error checking printer {printer_id} status: {str(e)}")
                status[printer_id] = 'Error'
        return status

    def check_printer_status(self, printer_ip, printer_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            try:
                sock.connect((printer_ip, printer_port))
                return True
            except Exception as e:
                logging.warning(f"Failed to connect to {printer_ip}:{printer_port} - {e}")
                return False

class PrintLabel(Resource, PrinterCommunicationMixin):
    method_decorators = [require_apikey]

    def post(self):
        try:
            errors = validate_request(request.json)
            if errors:
                return {'errors': errors}, 400

            data = request.json
            printer = self.get_printer_info(data['printer_id'])
            
            zpl_command = generate_zpl(**data)
            self.send_zpl_to_printer(printer['ip'], printer['port'], zpl_command)
            
            return {'message': 'Label sent to printer successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            logging.error(f"Error in PrintLabel: {str(e)}")
            return {'error': str(e)}, 500

class PrintMsl(Resource, PrinterCommunicationMixin):
    method_decorators = [require_apikey]

    def post(self):
        try:
            errors = validate_msl_request(request.json)
            if errors:
                return {'errors': errors}, 400

            data = request.json
            printer = self.get_printer_info(data['printer_id'])
            
            print_msl_command = generate_msl_sticker(**data)
            self.send_zpl_to_printer(printer['ip'], printer['port'], print_msl_command)
            
            return {'message': 'MSL label sent to printer successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            logging.error(f"Error in PrintMsl: {str(e)}")
            return {'error': str(e)}, 500

class PrintSpecialInstructions(Resource, PrinterCommunicationMixin):
    method_decorators = [require_apikey]

    def post(self):
        try:
            errors = validate_special_instructions_request(request.json)
            if errors:
                return {'errors': errors}, 400

            data = request.json
            printer = self.get_printer_info(data['printer_id'])
            
            print_command = generate_special_instructions_label(**data)
            self.send_zpl_to_printer(printer['ip'], printer['port'], print_command)
            
            return {'message': 'Special Instructions label sent to printer successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            logging.error(f"Error in PrintSpecialInstructions: {str(e)}")
            return {'error': str(e)}, 500

class PrintDry(Resource, PrinterCommunicationMixin):
    method_decorators = [require_apikey]

    def post(self):
        try:
            errors = validate_dry_request(request.json)
            if errors:
                return {'errors': errors}, 400

            data = request.json
            printer = self.get_printer_info(data['printer_id'])
            
            print_command = generate_dry_label(**data)
            self.send_zpl_to_printer(printer['ip'], printer['port'], print_command)
            
            return {'message': 'DRY label sent to printer successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            logging.error(f"Error in PrintDry: {str(e)}")
            return {'error': str(e)}, 500

class PrintTracescanLabel(Resource, PrinterCommunicationMixin):
    method_decorators = [require_apikey]

    def post(self):
        try:
            errors = validate_tracescan_request(request.json)
            if errors:
                return {'errors': errors}, 400

            data = request.json
            printer = self.get_printer_info(data['printer_id'])
            
            print_command = generate_tracescan_label(**data)
            self.send_zpl_to_printer(printer['ip'], printer['port'], print_command)
            
            return {'message': 'Tracescan label sent to printer successfully'}
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            logging.error(f"Error in PrintTracescanLabel: {str(e)}")
            return {'error': str(e)}, 500

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
api.add_resource(PrintMsl, '/print/msl')
api.add_resource(PrintSpecialInstructions, '/print/special-instructions')
api.add_resource(PrintDry, '/print/dry')
api.add_resource(PrintTracescanLabel, '/print/tracescan')

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
        host='0.0.0.0',
        port=int(os.getenv('FLASK_RUN_PORT', 5500))
    )
