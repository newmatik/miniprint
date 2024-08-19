# Request validation logic
def validate_request(data):
    required_fields = ['printer_id', 'batch', 'item_code', 'description_line1', 'description_line2', 'manufacturer', 'manufacturer_part_line1', 'manufacturer_part_line2', 'warehouse', 'parent_warehouse', 'msl', 'qty', 'date', 'user']
    missing = [field for field in required_fields if field not in data]
    return missing

# Validation logic for MSL print request
def validate_msl_request(data):
    required_fields = ['printer_id', 'msl', 'date', 'time']
    missing = [field for field in required_fields if field not in data]
    return missing

# Validation logic for special instructions print request
def validate_special_instructions_request(data):
    required_fields = ['printer_id', 'line_1', 'line_2', 'line_3', 'line_4', 'line_5']
    missing = [field for field in required_fields if field not in data]
    return missing
