# ZPL generation code
def generate_zpl(printer_id, batch, item_code, description_line1, description_line2, manufacturer, manufacturer_part, warehouse, parent_warehouse, msl, qty, date, user):
    # Generates the ZPL string...
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
    ^FO295,305^FDMSL {msl}^FS

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
    