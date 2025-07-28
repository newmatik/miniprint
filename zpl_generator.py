import re

def strip_or_empty(value: str) -> str:
    """Return stripped value or empty string if None.
    
    Args:
        value (str): The value to strip.
        
    Returns:
        str: The stripped value or empty string if None.
    """
    return value.strip() if value is not None else ''


def generate_zpl(
    printer_id: str,
    batch: str,
    item_code: str,
    description_line1: str,
    description_line2: str,
    manufacturer: str,
    manufacturer_part_line1: str,
    manufacturer_part_line2: str,
    warehouse: str,
    parent_warehouse: str,
    msl: str,
    qty: str,
    date: str,
    user: str,
    ) -> str:
    """
    Generate ZPL command for printing standard batch labels.
    Uses UTF-8 encoding (^CI28) to support German characters.

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
    ^CI28

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


def generate_msl_sticker(
    printer_id: str,
    msl: str,
    date: str,
    time: str,
    ) -> str:
    """
    Generate ZPL command for printing MSL stickers.
    Uses UTF-8 encoding (^CI28) to support German characters.

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
    ^CI28

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
    printer_id: str,
    line_1: str,
    line_2: str,
    line_3: str,
    line_4: str,
    line_5: str,
    line_6: str,
    line_7: str,
    line_8: str,
    line_9: str,
    line_10: str,
    line_11: str,
    line_12: str,
    ) -> str:
    """
    Generate ZPL command for printing special instructions label.
    Uses UTF-8 encoding (^CI28) to support German characters.

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
    ^CI28

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


def generate_dry_label(printer_id: str) -> str:
    """
    Generate ZPL command for printing DRY label.
    Uses UTF-8 encoding (^CI28) to support German characters.

    Note: There are no variables because the details will be filled in by the users.

    Args:
        printer_id (str): The printer ID.

    Returns:
        str: The ZPL command for printing the DRY label.
    """

    return """
    ^XA
    ^CI28

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
    Uses UTF-8 encoding (^CI28) to support German characters.

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
    ^CI28

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


def generate_svt_fortlox_label_ok(
    printer_id: str,
    sv_article_no: str,
    serial_no: str,
    fw_version: str,
    run_date: str,
) -> str:
    """
    Generate ZPL command for printing SVT Fortlox label.
    The dynamic data comes from the Laser.

    Args:
        printer_id (str): The printer ID.
        sv_article_no (str): Customer SVT's article number.
        serial_no (str): The serial number.
        fw_version (str): The firmware version.
        run_date (str): The run date.

    Returns:
        str: The ZPL command for printing the SVT Fortlox label.
    """

    phib = "PHIB"
    phia = "PHIA"
    phii = "PHII"
    datamatrix_data = f"{sv_article_no}|{phib}|{serial_no}|{fw_version}|{phia}|||{phii}|||"

    return f"""
    ^XA
    ^CI28

    ^FX SV-ArtikelNr (Arial Bold)
    ^FO30,50
    ^A@N,30,30,E:71028264.TTF
    ^FD{sv_article_no}^FS

    ^FX FORTLOX Key Text (Arial Bold)
    ^FO30,90
    ^A@N,36,36,E:71028264.TTF
    ^FDFORTLOX Key^FS

    ^FX WEEE Disposal Symbol Image
    ^FO30,150
    ^GFA,1130,1130,10,,8X01CX03EX063X0C38V0181CV03,0EM0FFEL06,07K01JF8K0C,038I03LF8I018,01CI07FDJFEI03,00EI0FC0FFE0F9806,007003FCK03FC0C,003003FCK01FE18,001807FEK01FE3,I0E1PFE6,I060PFCC,I0307N0E18,I0187N0E3,J0C3N0E7,J063N0FE,J033M01FE,J01FM01FE,K0FM01EE,K07M01E6,K078L01EE,K038L03FE,K01CL07FE,K01E007FF8FC,K01F00IFD9C,K01F80JF18,K019C0IFE18,K018E0IFE18,K0187I03C18,K01838003018,K01C18006018,K01C0E00E018,K01C0601C038,L0C03038038,L0C0187003,L0C00CE003,L0C007C003,L0C0078003,:L0C00FC003,L0C01C6003,L0C0383003,L0E0703803,L0E0E00C03,L0E1C00E07,L0E3800707,L0E7I0387,L07EI01C7,L07CJ0E6,L078J07E,L07K03E,L0EK01E,K01EL0E,K03EL0F,K07EL0F,K0E7K01F8,J01C7K07FC,J0383K0FFE,J0703J01IF,J0E03J01F1F8,I01C03J01DFFC,I038038I03DFFE,I07003IFEFDFF3,I0E003MFE18,001C001MFE0C,0038001FJ0FFC0E,007I01EJ07F807,00EI01EJ01F0038,01CS01C,038T0E,07U07,0EU038,1CU01C,18V0C,3W04,,::::::::::::::::01VF,03VF8,::::::::::::::^FS

    ^FX CE Marking Image
    ^FO180,203
    ^GFA,660,660,11,K01FFP03FE,K07FFO01FFE,J03IFO07FFE,J0JFN03IFE,I03JFN07IFE,I07JFM01JFE,001KFM03JFE,003KFM07JFE,007KFM0KFE,00JF8M01JF,01IFCN03IF8,03IFO07FFC,03FFCO0IF8,07FF8N01FFE,0IFO01FFC,0FFEO03FF8,1FFCO03FF,1FF8O07FE,3FFP07FE,3FFP0FFC,3FEP0FFC,7FEP0FF8,7FCO01FF8,7FCO01FF,FFCO01FF,FF8O01KFC,FF8O01LF8,:::::::FF8O01FFC,FFCO01FF,7FCO01FF,7FCO01FF8,7FEP0FF8,3FEP0FFC,3FFP0FFC,3FFP07FE,1FF8O07FE,1FFCO03FF,0FFEO03FF8,0IFO01FFC,07FF8N01FFE,03FFCO0IF8,03IFO07FFC,01IFCN03IF8,00JF8M01JF,007KFM0KFE,003KFM07JFE,001KFM03JFE,I07JFM01JFE,I03JFN07IFE,J0JFN03IFE,J03IFO07FFE,K07FFO01FFE,K01FFP03FE,^FS

    ^FX DataMatrixCode ECC Typ 200
    ^FO315,90
    ^BXN,6,200
    ^FD{datamatrix_data}^FS

    ^FX Vertical Line
    ^FO564,0
    ^GB1,360,1,B^FS

    ^FX FW-Version Label (rotated Arial)
    ^FO690,55
    ^A@L,26,26,E:71028264.TTF
    ^FDFW:^FS

    ^FX FW-Version Value (rotated Arial Bold)
    ^FO720,55
    ^A@L,26,26,E:71028264.TTF
    ^FD{fw_version}^FS

    ^FX Run Date Label (rotated Arial)
    ^FO690,150
    ^A@L,26,26,E:71028264.TTF
    ^FDDATE:^FS

    ^FX Run Date Value (rotated Arial Bold)
    ^FO720,150
    ^A@L,26,26,E:71028264.TTF
    ^FD{run_date}^FS

    ^FX SV Logo at bottom
    ^FO30,308
    ^GFA,874,874,38,N0F8gQ03KFE,01FFE001F8gQ07LF00F8I0F8,0JFC01F8gQ07LF81FC001FC,1KFgU07LF81FC001FC,3F807FgU07LF80FC001F8,7F003FgU07LF00FE003F8,7FL0F80F83F80FEI07FE001F03F8001FFR07E003F00FFCI03FFI01FF8,7F8J01F81FDFFC7FF001IFC01F9FFE00IFEQ07E007F03IFI0IFC007FFE,3FEJ01FC1NF807JF01KF03FC7FQ03F007E0JFC03F8FF01FC7F8,1FFEI01FC1FF8FFE3FC0FE07F81FF87F03F00E007LF003F00FE1FC0FE07F01E03F007,0IFC001FC1FE07FC1FC1FC01F81FE03F83FK07LF801F80FC3F807F07EJ03F,01IFC01FC1FC07F00FC1F801FC1F803F83F8J07LF801F80FC7F003F87FJ03F8,001IF01FC1F807F00FC3F800FC1F801F83FFCI07LFI0FC1F87E001F83FF8001FFC,I07FF81FC1F807F00FC3F800FC1F801F80IFCR0FC1F87E001F81IF800IFC,J07FC1FC1F807F00FC3F800FC1F801F803IF8Q0FC1F07E001F807IF003IF8,J01FC1FC1F807F00FC3F800FC1F801F8I0FFCQ07E3F07E001F8001FF8I0FFC,J01FC1FC1F807F00FC3F800FC1F801F8I01FC03LFI07E3E07E003F8I03FCI01FE,1C001FC1FC1F807F00FC1F801FC1F801F8J0FE07LF8003E7E07F003F8I01FCJ0FE,7F003F81FC1F807F00FC1FC03F81F801F8J0FC03KFEI01FFC03F807FJ01FCJ0FE,3FC0FF01FC1F807F00FC0FF07F01F801F81F01FCQ01FFC01FC0FE03E01F81F00FC,1JFE01FC1F807F00FC07IFE01F801F81JF8Q01FF800JFC03JF01JF8,07IF800F80F803E00FC01IF801F801F807FFES0FF8003IFI0IFC007FFE,00FFCI07S03FCP01FFI07LFJ07EJ07F8I01FEJ0FF,^FS

    ^XZ
    """


def generate_svt_fortlox_label_nok(
    printer_id: str,
    sv_article_no: str,
    error_code: str,
    error_date: str,
    error_time: str,
    frequency_tolerance: str,
    serial_no: str,
) -> str:
    """
    Generate ZPL command for printing error codes for the SVT Fortlox label.
    The dynamic data comes from the Laser.

    Args:
        printer_id (str): The printer ID.
        sv_article_no (str): Customer SVT's article number.
        error_code (str): The error code.
        error_date (str): The error date.
        error_time (str): The error time.
        frequency_tolerance (str): The frequency tolerance.
        serial_no (str): The serial number.

    Returns:
        str: The ZPL command for printing the error codes for the SVT Fortlox label.
    """

    return f"""
    ^XA
    ^CI28

    ^FX SV ARTICLE NUMBER (Arial Bold)
    ^FO30,30
    ^A@N,21,21,E:71028264.TTF
    ^FD{sv_article_no}^FS

    ^FX ERROR CODE (Arial)
    ^FO30,70
    ^A@N,20,20,E:85620388.TTF
    ^FDERROR CODE: ^FS

    ^FX ERROR CODE VALUE(Arial Bold)
    ^FO180,70
    ^A@N,21,21,E:71028264.TTF
    ^FD{error_code}^FS

    ^FX DATE AND TIME (Arial)
    ^FO30,110
    ^A@N,20,20,E:85620388.TTF
    ^FDDate (Time): ^FS

    ^FX DATE AND TIME VALUE (Arial Bold)
    ^FO180,110
    ^A@N,21,21,E:71028264.TTF
    ^FD{error_date} ({error_time})^FS

    ^FX FREQUENCY TOLERANCE (Arial)
    ^FO30,150
    ^A@N,20,20,E:85620388.TTF
    ^FDFrequency Tolerance: ^FS

    ^FX FREQUENCY TOLERANCE VALUE (Arial Bold)
    ^FO250,150
    ^A@N,21,21,E:71028264.TTF
    ^FD{frequency_tolerance} ppm^FS

    ^FX SERIAL NUMBER (Arial)
    ^FO30,190
    ^A@N,20,20,E:85620388.TTF
    ^FDSerial: ^FS

    ^FX SERIAL NUMBER VALUE (Arial Bold)
    ^FO130,190
    ^A@N,21,21,E:71028264.TTF
    ^FD{serial_no}^FS

    ^XZ
    """
