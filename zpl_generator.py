import re

def strip_or_empty(value):
    """Return stripped value or empty string if None.
    
    Args:
        value (str): The value to strip.
        
    Returns:
        str: The stripped value or empty string if None.
    """
    return value.strip() if value is not None else ''


def generate_zpl(
    printer_id,
    batch,
    item_code,
    description_line1,
    description_line2,
    manufacturer,
    manufacturer_part_line1,
    manufacturer_part_line2,
    warehouse,
    parent_warehouse,
    msl,
    qty,
    date,
    user
    ) -> str:
    """
    Generate ZPL command for printing standard batch labels.

    Args:
        printer_id (str): The printer ID.
        batch (str): The batch number.
        item_code (str): The item code.
        description_line1 (str): The first line of the description.
        description_line2 (str): The second line of the description.
        manufacturer (str): The manufacturer.
        manufacturer_part_line1 (str): The first line of the manufacturer's part number.
        manufacturer_part_line2 (str): The second line of the manufacturer's part number.
        warehouse (str): The warehouse.
        parent_warehouse (str): The parent warehouse.
        msl (str): The MSL level.
        qty (str): The quantity.
        date (str): The date.
        user (str): The user.

    Returns:
        str: The ZPL command for printing the standard batch label.
    """

    # Remove leading and trailing spaces
    batch = strip_or_empty(batch)
    item_code = strip_or_empty(item_code)
    description_line1 = strip_or_empty(description_line1)
    description_line2 = strip_or_empty(description_line2)
    manufacturer = strip_or_empty(manufacturer)
    manufacturer_part_line1 = strip_or_empty(manufacturer_part_line1)
    manufacturer_part_line2 = strip_or_empty(manufacturer_part_line2)
    warehouse = strip_or_empty(warehouse)
    parent_warehouse = strip_or_empty(parent_warehouse)
    msl = strip_or_empty(msl)
    user = strip_or_empty(user)
    
    # Check if msl is a single digit or double digit and adjust the box size accordingly
    if len(msl) == 2:
        box = "^FO280,280^GB130,68,5,B,0^FS"
    else:
        box = "^FO280,280^GB110,68,5,B,0^FS"
    
    # Shorten warehouse name for Incoming Goods
    if warehouse == 'Incoming Goods':
        warehouse = 'Incoming'

    # Shorten parent warehouse name for All Warehouses and Kommissioniert
    if parent_warehouse == 'All Warehouses':
        parent_warehouse = 'All WH'
    elif (parent_warehouse == 'Kommissioniert-RO' or parent_warehouse == 'Kommissioniert-DE'):
        parent_warehouse = 'Kommissioniert'
    
    # Check if warehouse is long and adjust the font size accordingly
    if len(warehouse) > 7:
        warehouse = f"^CF0,30^FO280,200^FD{warehouse}^FS"
        parent_warehouse_yposition = '230'
    else:
        warehouse = f"^CF0,40^FO280,200^FD{warehouse}^FS"
        parent_warehouse_yposition = '240'
    
    # Check if parent warehouse is long and adjust the font size accordingly
    if len(parent_warehouse) > 9:
        parent_warehouse = f"^CF0,20^FO280,{parent_warehouse_yposition}^FD{parent_warehouse}^FS"
    else:
        parent_warehouse = f"^CF0,30^FO280,{parent_warehouse_yposition}^FD{parent_warehouse}^FS"
    
    # If manufacturer and manufacturer part number are empty, print as "None" instead of "empty"
    if manufacturer == '' and manufacturer_part_line1 == '' and manufacturer_part_line2 == '':
        manufacturer = 'None' # Print None to inform user that there is no MPN for the batch
        manufacturer_part_line1 = '' # Leave empty to avoid printing "None" multiple times (will look redundant)
        manufacturer_part_line2 = '' # Leave empty to avoid printing "None" multiple times (will look redundant)

    # Return the ZPL command
    return f"""
    ^XA

    ^FO280,10
    ^BQN,2,5,H
    ^FDMM,A{batch}^FS

    ^CF0,20
    ^FO20,20^FDBatch^FS
    ^CF0,60
    ^FO20,45^FD{batch}^FS

    ^CF0,20
    ^FO20,105^FDItem Code^FS
    ^CF0,40
    ^FO20,130^FD{item_code}^FS

    ^CF0,20
    ^FO20,175^FDDescription^FS
    ^CF0,20
    ^FO20,200^FD{description_line1}^FS
    ^FO20,220^FD{description_line2}^FS

    ^CF0,20
    ^FO20,250^FDManufacturer^FS
    ^CF0,20
    ^FO20,275^FD{manufacturer}^FS
    ^FO20,295^FD{manufacturer_part_line1}^FS
    ^FO20,315^FD{manufacturer_part_line2}^FS

    ^CF0,20
    ^FO280,175^FDIncoming^FS
    {warehouse}
    {parent_warehouse}

    ^CF0,30
    {box}
    ^FO295,300^FDMSL {msl}^FS

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


def generate_msl_sticker(printer_id, msl, date, time):
    """
    Generate ZPL command for printing MSL stickers.

    Args:
        printer_id (str): The printer ID.
        msl (str): The MSL level.
        date (str): The date.
        time (str): The time.

    Returns:
        str: The ZPL command for printing the MSL sticker.
    """

    # Remove the "MSL " prefix because this is already in the ZPL command
    msl = msl.replace('MSL ', '')

    # Update the mounting time based on the MSL level
    if msl == '1':
        mounting_time = 'Unlimited'
    elif msl == '2':
        mounting_time = '1 year'
    elif msl == '2A':
        mounting_time = '4 weeks'
    elif msl == '3':
        mounting_time = '168 hours (7 days)'
    elif msl == '4':
        mounting_time = '72 hours (3 days)'
    elif msl == '5':
        mounting_time = '48 hours (2 days)'
    elif msl == '5A':
        mounting_time = '24 hours (1 day)'
    elif msl == '6':
        mounting_time = 'Bake before use'

    # Check if msl is a single digit or double digit and adjust the position accordingly
    if len(msl) == 2:
        msl_print = f"^CF0,80^FO265,30^FD{msl}^FS"
    else:
        msl_print = f"^CF0,80^FO285,30^FD{msl}^FS"

    # Return the ZPL command
    return f"""
    ^XA

    ^FX Large Text MSL
    ^CF0,80^FO85,30^FDMSL^FS

    ^FX Large Text MSL Number
    ^CF0,80^FO285,30^FD{msl_print}^FS

    ^FX Horizontal Line 1
    ^FO10,110^GB430,1,1^FS

    ^FX Texts Bag Seal Date and Time
    ^CF0,20^FO25,130^FDBag Seal Date:^FS
    ^CF0,20^FO98,170^FDTime:^FS

    ^FX Vertical Line 1
    ^FO303,115^GB3,80,3^FS

    ^FX Horizontal Line 2
    ^FO10,200^GB430,1,1^FS

    ^FX Mounting Time
    ^CF0,20^FO25,220^FDMounting after opening: {mounting_time}^FS

    ^FX Horizontal Line 3
    ^FO10,255^GB430,1,1^FS

    ^FX Texts Bag Open Date and Time
    ^CF0,20^FO25,275^FDBag Open Date:^FS
    ^CF0,20^FO104,315^FDTime:^FS

    ^FX Texts Expiration Date and Time
    ^CF0,20^FO25,355^FDExpiration Date:^FS
    ^CF0,20^FO108,395^FDTime:^FS

    ^FX Vertical Line 2
    ^FO303,265^GB3,155,3^FS

    ^FX Black Box Negative (Must be last, otherwise it will make other lines negative as well)
    ^LRY
    ^FO250,5
    ^GB109,105,95^FS

    ^XZ
    """


def generate_special_instructions_label(
    printer_id,
    line_1,
    line_2,
    line_3,
    line_4,
    line_5,
    line_6,
    line_7,
    line_8,
    line_9,
    line_10,
    line_11,
    line_12
    ) -> str:
    """
    Generate ZPL command for printing special instructions label.

    Note: The special instructions are split into multiple lines (maximum 12 lines)
    by the frontend.

    Args:
        printer_id (str): The printer ID.
        line_1 (str): The first line of special instructions.
        line_2 (str): The second line of special instructions.
        line_3 (str): The third line of special instructions.
        line_4 (str): The fourth line of special instructions.
        line_5 (str): The fifth line of special instructions.
        line_6 (str): The sixth line of special instructions.
        line_7 (str): The seventh line of special instructions.
        line_8 (str): The eighth line of special instructions.
        line_9 (str): The ninth line of special instructions.
        line_10 (str): The tenth line of special instructions.
        line_11 (str): The eleventh line of special instructions.
        line_12 (str): The twelfth line of special instructions.

    Returns:
        str: The ZPL command for printing the special instructions label.
    """

    return f"""
    ^XA

    ^FX Bounding Box
    ^FO10,10^GB380,380,1,B,0^FS

    ^FX Special Instructions Header
    ^CF0,40, 45
    ^FO23,25^FDSpecial Instructions^FS

    ^FX Special Instructions Text
    ^CF0,25^FO25,90^FD{line_1}^FS
    ^CF0,25^FO25,115^FD{line_2}^FS
    ^CF0,25^FO25,140^FD{line_3}^FS
    ^CF0,25^FO25,165^FD{line_4}^FS
    ^CF0,25^FO25,190^FD{line_5}^FS
    ^CF0,25^FO25,215^FD{line_6}^FS
    ^CF0,25^FO25,240^FD{line_7}^FS
    ^CF0,25^FO25,265^FD{line_8}^FS
    ^CF0,25^FO25,290^FD{line_9}^FS
    ^CF0,25^FO25,315^FD{line_10}^FS
    ^CF0,25^FO25,340^FD{line_11}^FS
    ^CF0,25^FO25,365^FD{line_12}^FS

    ^FX Black Box Negative for Cell
    ^LRY
    ^FO11,11
    ^GB378,59,59^FS

    ^XZ
    """


def generate_dry_label(printer_id) -> str:
    """
    Generate ZPL command for printing DRY label.

    Note: There are no variables because the details will be filled in by the users.

    Args:
        printer_id (str): The printer ID.

    Returns:
        str: The ZPL command for printing the DRY label.
    """

    return """
    ^XA

    ^FX Large Text DRY
    ^CF0,90^FO140,30^FDDRY^FS

    ^FX Horizontal Line 1
    ^FO10,120^GB430,1,1^FS

    ^FX Texts Start Date and Time
    ^CF0,20^FO25,140^FDTemperature:^FS
    ^CF0,20^FO47,180^FDStart Date:^FS
    ^CF0,20^FO87,220^FDTime:^FS

    ^FX Horizontal Line 2
    ^FO10,250^GB430,1,1^FS

    ^FX Texts End Date and Time
    ^CF0,20^FO54,270^FDEnd Date:^FS
    ^CF0,20^FO86,310^FDTime:^FS

    ^FX Text Duration
    ^CF0,20^FO57,350^FDDuration:^FS

    ^FX Horizontal Line 3
    ^FO10,385^GB430,1,1^FS

    ^FX Vertical Line
    ^FO303,125^GB3,255,3^FS

    ^XZ
    """


def validate_serial_number(serial: str) -> bool:
    """Validate serial number format and length for Code128 barcode.
    
    Args:
        serial (str): The serial number to validate.
        
    Returns:
        bool: True if the serial number is valid, False otherwise.
    """
    # Check format matches pattern: 5 digits-11 digits
    if not re.match(r'^\d{5}-\d{11}$', serial):
        raise ValueError("Serial number must be in format: XXXXX-XXXXXXXXXXX")
    
    # Code128 has practical length limits for reliable scanning
    if len(serial) > 17:
        raise ValueError("Serial number exceeds maximum length for reliable scanning")
    
    return True


# ZPL generation code for CDS Tracescan Label
def generate_tracescan_label(
    printer_id: str,
    hw_version: str,
    sw_version: str,
    standard_indicator: str,
    wo_serial_number: str,
    ginv_description: str,
    ginv_serial: str,
    ioca_description: str,
    ioca_serial: str,
    mcua_description: str,
    mcua_serial: str,
    lcda_description: str,
    lcda_serial: str,
    ) -> str:
    """
    Generate ZPL command for printing tracescan label.

    Args:
        printer_id (str): The printer ID.
        hw_version (str): The hardware version.
        sw_version (str): The software version.
        standard_indicator (str): The standard indicator.
        wo_serial_number (str): The work order serial number.
        ginv_description (str): The ginv description.
        ginv_serial (str): The ginv serial.
        ioca_description (str): The ioca description.
        ioca_serial (str): The ioca serial.
        mcua_description (str): The mcua description.
        mcua_serial (str): The mcua serial.
        lcda_description (str): The lcda description.
        lcda_serial (str): The lcda serial.

    Returns:
        str: The ZPL command for printing the tracescan label.
    """
    # Validate serial number
    validate_serial_number(wo_serial_number)

    # Change "GaN Inverter" to "GINV" to protect confidential customer information
    ginv_description = ginv_description.replace("GaN Inverter", "GINV")

    # Strip leading and trailing spaces and replace dashes with spaces
    ginv_description = ginv_description.strip().replace("-", " ").upper()
    ioca_description = ioca_description.strip().replace("-", " ").upper()
    mcua_description = mcua_description.strip().replace("-", " ").upper()
    lcda_description = lcda_description.strip().replace("-", " ").upper()

    return f"""
    ^XA

    ^FX Item Description
    ^CFP,30,30
    ^FO60,20^FDAssembly CND{standard_indicator} (HW {hw_version}, SW{sw_version})^FS

    ^FX Code128 with WO Serial Number
    ^BY2,3,10
    ^FO60,65
    ^BCN,80,Y,N,N
    ^FD{wo_serial_number}^FS

    ^FX GINV Details
    ^CFP,15
    ^FO60,185^FD{ginv_description}^FS
    ^FO60,205^FD{ginv_serial}^FS

    ^FX IOCA Details
    ^CFP,15
    ^FO60,225^FD{ioca_description}^FS
    ^FO60,245^FD{ioca_serial}^FS

    ^FX MCUA Details
    ^CFP,15
    ^FO330,185^FD{mcua_description}^FS
    ^FO330,205^FD{mcua_serial}^FS

    ^FX LCDA Details
    ^CFP,15
    ^FO330,225^FD{lcda_description}^FS
    ^FO330,245^FD{lcda_serial}^FS

    ^XZ
    """
