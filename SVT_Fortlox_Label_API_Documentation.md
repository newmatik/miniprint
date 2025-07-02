# SVT Fortlox Label Printing API Documentation

## Overview
This API endpoint allows you to automatically print SVT Fortlox labels after successful assembly programming. The endpoint generates and sends ZPL (Zebra Programming Language) commands to designated label printers.

## Integration Workflow
1. Your assembly programming completes successfully
2. Your program calls this API endpoint with the required parameters
3. The API generates a label with DataMatrix code, WEEE symbol, CE marking, and SV logo
4. The label is automatically sent to the specified printer

---

## API Endpoint Details

### **POST** `/print/svt-fortlox`

**Base URL:** `http://your-server-ip:5500`

### Authentication
- **Method:** API Key in header
- **Header:** `apikey: YOUR_API_KEY`
- **Content-Type:** `application/json`

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `printer_id` | string | ✅ | Printer identifier | `"prt-label-SVT"` |
| `sv_article_no` | string | ✅ | Customer SVT's article number | `"SVT-12345"` |
| `serial_no` | string | ✅ | Assembly serial number | `"98765-43210987654"` |
| `fw_version` | string | ✅ | Firmware version | `"v2.1.0"` |
| `run_date` | string | ✅ | Programming/test date | `"2024-12-19"` |

### Available Printers

| Printer ID | Location | IP Address |
|------------|----------|------------|
| `prt-label-SVT` | SVT Station | 10.1.0.53 |
| `prt-label-CDS` | CDS Station | 10.1.0.53 |

---

## Request Example

```http
POST http://your-server-ip:5500/print/svt-fortlox
Content-Type: application/json
apikey: YOUR_API_KEY

{
  "printer_id": "prt-label-SVT",
  "sv_article_no": "SVT-12345",
  "serial_no": "98765-43210987654",
  "fw_version": "v2.1.0",
  "run_date": "2024-12-19"
}
```

---

## Response Examples

### Success Response (200 OK)
```json
{
  "message": "SVT Fortlox label sent to printer successfully"
}
```

### Error Responses

#### Missing/Invalid API Key (403 Forbidden)
```json
{
  "error": "Invalid API key"
}
```

#### Missing Required Fields (400 Bad Request)
```json
{
  "errors": ["sv_article_no", "serial_no"]
}
```

#### Printer Not Found (404 Not Found)
```json
{
  "error": "Printer ID not found"
}
```

#### Printer Connection Error (500 Internal Server Error)
```json
{
  "error": "Printer connection timeout"
}
```

---

## Label Content
The printed label includes:
- **SV Article Number** (top left)
- **"FORTLOX Key" text** (below article number)
- **WEEE Disposal Symbol** (recycling icon)
- **CE Marking** (compliance symbol)
- **DataMatrix Code** (contains: `sv_article_no|PHIB|serial_no|fw_version|PHIA|||PHII|||`)
- **Firmware Version** (right side: `FW: v2.1.0`)
- **Run Date** (right side: `DATE: 2024-12-19`)
- **SV Company Logo** (bottom)

### Testing Connectivity
```bash
# Test server availability
curl -X GET http://your-server-ip:5500/ping

# Test printer status
curl -X GET http://your-server-ip:5500/printers/status \
  -H "apikey: YOUR_API_KEY"
```