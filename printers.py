import json
import logging
import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any

_LOCAL_FALLBACK_PRINTERS: Dict[str, Dict[str, Any]] = {
    'prt-batch-TWR1': {'ip': '10.1.0.48', 'port': 9100},
    'prt-batch-TWR2': {'ip': '10.1.0.49', 'port': 9100},
    'prt-batch-WE1': {'ip': '10.1.0.25', 'port': 9100},
    'prt-batch-WE2': {'ip': '10.1.0.26', 'port': 9100},
    'prt-batch-WE3': {'ip': '10.1.0.27', 'port': 9100},
    'prt-batch-WE4': {'ip': '10.1.0.28', 'port': 9100},
    'prt-label-CDS': {'ip': '10.1.0.53', 'port': 9100},
    'prt-K-SVT-00028': {'ip': '10.1.0.56', 'port': 9100},  # SVT "test ok" label (60x30mm)
    'prt-K-SVT-00029': {'ip': '10.1.0.57', 'port': 9100},  # SVT "not ok" label (51x25mm, removable)
    'prt-batch-RO1': {'ip': '192.168.120.9', 'port': 9100},
}


def _get_env(name: str, default: str = "") -> str:
    """Get environment variable with fallback"""
    value = os.getenv(name)
    return value if value is not None and value != "" else default


def _load_printers_from_erp() -> Dict[str, Dict[str, Any]]:
    """Get list of printers from ERPNext"""
    try:
        load_dotenv()
    except Exception:
        pass
    erp_url = _get_env('ERP_URL')
    api_key = _get_env('ERP_API_KEY')
    api_secret = _get_env('ERP_API_SECRET')
    doctype = _get_env('ERP_PRINTER_DOCTYPE', 'NPrint Printer')

    if not (erp_url and api_key and api_secret):
        logging.info("ERP config not found; using local fallback printers")
        return {}

    url = erp_url.rstrip('/') + f"/api/resource/{doctype}"

    requested_fields = ['printer_name', 'server_ip', 'port']

    params = {
        'fields': json.dumps(requested_fields),
        'limit_page_length': 1000,
    }

    headers = {
        'Authorization': f"token {api_key}:{api_secret}"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        rows = response.json().get('data', [])
    except Exception as exc:
        logging.warning(f"Failed to load printers from ERP ({doctype}): {exc}")
        return {}

    result: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        printer_id = row.get('printer_name')
        server_ip = row.get('server_ip')
        if not printer_id or not server_ip:
            continue

        try:
            port = int(row.get('port')) if row.get('port') is not None else 9100
        except Exception:
            port = 9100

        result[str(printer_id)] = {'ip': str(server_ip), 'port': port}

    return result


def _build_printers_mapping() -> Dict[str, Dict[str, Any]]:
    """Build printers mapping from ERP"""
    erp_printers = _load_printers_from_erp()
    if erp_printers:
        logging.info(f"Loaded {len(erp_printers)} printers from ERP")
        return erp_printers

    logging.info("Using local fallback printers configuration")
    return _LOCAL_FALLBACK_PRINTERS

# Public mapping used by the app
printers: Dict[str, Dict[str, Any]] = {}
printers.update(_build_printers_mapping())


def refresh_printers_from_erp() -> None:
    """Reload printers from ERP into the global mapping. Keeps fallback if ERP yields nothing."""
    erp_printers = _load_printers_from_erp()
    if erp_printers:
        printers.clear()
        printers.update(erp_printers)
        logging.info(f"Refreshed printers from ERP: {len(printers)} entries")
    else:
        logging.info("ERP refresh returned no data; keeping existing printers mapping")
