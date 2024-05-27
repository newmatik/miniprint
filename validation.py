# Request validation logic
def validate_request(data):
    required_fields = ['printer_id', 'batch', 'item_code', 'description_line1', 'description_line2', 'manufacturer', 'manufacturer_part_line1', 'manufacturer_part_line2', 'warehouse', 'parent_warehouse', 'msl', 'qty', 'date', 'user']
    missing = [field for field in required_fields if field not in data]
    return missing
