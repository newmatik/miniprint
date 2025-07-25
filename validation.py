from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class FieldRequirement(Enum):
    """Enum for field requirements"""
    REQUIRED = "required"
    OPTIONAL = "optional"

@dataclass
class ValidationRule:
    """Validation rule for a field"""
    name: str
    requirement: FieldRequirement = FieldRequirement.REQUIRED

class RequestValidator:
    """Base validator class for all request types"""
    
    def __init__(self, rules: List[ValidationRule]):
        self.rules = rules
        self._required_fields = [rule.name for rule in rules 
                               if rule.requirement == FieldRequirement.REQUIRED]

    def validate(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate the request data against the rules
        
        Args:
            data: Dictionary containing the request data
            
        Returns:
            List of missing required fields
        """
        if not isinstance(data, dict):
            raise ValidationError("Input data must be a dictionary")
            
        return [field for field in self._required_fields if field not in data]

# Predefined validators for different request types
STANDARD_VALIDATOR = RequestValidator([
    ValidationRule("printer_id"),
    ValidationRule("batch"),
    ValidationRule("item_code"),
    ValidationRule("description_line1"),
    ValidationRule("description_line2"),
    ValidationRule("manufacturer"),
    ValidationRule("manufacturer_part_line1"),
    ValidationRule("manufacturer_part_line2"),
    ValidationRule("warehouse"),
    ValidationRule("parent_warehouse"),
    ValidationRule("msl"),
    ValidationRule("qty"),
    ValidationRule("date"),
    ValidationRule("user"),
])

MSL_VALIDATOR = RequestValidator([
    ValidationRule("printer_id"),
    ValidationRule("msl"),
    ValidationRule("date"),
    ValidationRule("time"),
])

SPECIAL_INSTRUCTIONS_VALIDATOR = RequestValidator([
    ValidationRule("printer_id")] + 
    [ValidationRule(f"line_{i}") for i in range(1, 13)]
)

DRY_VALIDATOR = RequestValidator([
    ValidationRule("printer_id"),
])

TRACESCAN_VALIDATOR = RequestValidator([
    ValidationRule("printer_id"),
    ValidationRule("hw_version"),
    ValidationRule("sw_version"),
    ValidationRule("standard_indicator"),
    ValidationRule("wo_serial_number"),
    ValidationRule("ginv_description"),
    ValidationRule("ginv_serial"),
    ValidationRule("ioca_description"),
    ValidationRule("ioca_serial"),
    ValidationRule("mcua_description"),
    ValidationRule("mcua_serial"),
    ValidationRule("lcda_description"),
    ValidationRule("lcda_serial"),
])

SVT_FORTLOX_OK_VALIDATOR = RequestValidator([
    ValidationRule("printer_id"),
    ValidationRule("sv_article_no"),
    ValidationRule("serial_no"),
    ValidationRule("fw_version"),
    ValidationRule("run_date"),
])


def validate_request(data: Dict[str, Any]) -> List[str]:
    """Validate standard print request"""
    return STANDARD_VALIDATOR.validate(data)


def validate_msl_request(data: Dict[str, Any]) -> List[str]:
    """Validate MSL print request"""
    return MSL_VALIDATOR.validate(data)


def validate_special_instructions_request(data: Dict[str, Any]) -> List[str]:
    """Validate special instructions print request"""
    return SPECIAL_INSTRUCTIONS_VALIDATOR.validate(data)


def validate_dry_request(data: Dict[str, Any]) -> List[str]:
    """Validate DRY print request"""
    return DRY_VALIDATOR.validate(data)


def validate_tracescan_request(data: Dict[str, Any]) -> List[str]:
    """Validate Tracescan Label print request"""
    return TRACESCAN_VALIDATOR.validate(data)


def validate_svt_fortlox_request_ok(data: Dict[str, Any]) -> List[str]:
    """Validate SVT Fortlox OK print request"""
    return SVT_FORTLOX_OK_VALIDATOR.validate(data)
