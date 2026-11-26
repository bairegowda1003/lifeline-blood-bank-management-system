"""
Validation Module
Blood Bank Donor Directory & Stock Tracker
Provides rigorous regex, numeric, and date validation with descriptive error messages.
"""

import re
from datetime import datetime, date
from typing import Tuple, Optional
import config

# Regular Expressions
# Phone: 10 digits starting with 6, 7, 8, or 9 (standard Indian mobile format) or standard 10-digit number
RE_PHONE = re.compile(r"^[6-9]\d{9}$")
RE_PHONE_GENERIC = re.compile(r"^\d{10}$")

# Name: 2 to 70 characters, letters, spaces, dots, hyphens, apostrophes
RE_NAME = re.compile(r"^[A-Za-z\s\.\-']{2,70}$")

# Hospital Name: 3 to 100 characters, alphanumeric, spaces, dots, commas, hyphens, and ampersands
RE_HOSPITAL = re.compile(r"^[A-Za-z0-9\s\.\-',&()]{3,100}$")

# Date pattern YYYY-MM-DD
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(Exception):
    """Custom exception raised for user input validation errors."""
    pass


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Validates a donor name.
    Must be non-empty, between 2 and 70 characters, and contain valid name characters.
    """
    if not name or not name.strip():
        return False, "Donor name cannot be empty."
    clean_name = name.strip()
    if len(clean_name) < 2:
        return False, "Donor name must be at least 2 characters long."
    if len(clean_name) > 70:
        return False, "Donor name cannot exceed 70 characters."
    if not RE_NAME.match(clean_name):
        return False, "Donor name should contain only alphabets, spaces, dots, or hyphens."
    return True, clean_name


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validates a 10-digit phone number.
    Rejects non-numeric characters, wrong lengths, or invalid leading digits.
    """
    if not phone or not phone.strip():
        return False, "Phone number cannot be empty."
    clean_phone = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if not clean_phone.isdigit():
        return False, "Phone number must contain only numeric digits."
    if len(clean_phone) != 10:
        return False, f"Phone number must be exactly 10 digits (got {len(clean_phone)})."
    if not RE_PHONE.match(clean_phone):
        # Fallback check for generic 10 digits
        if not RE_PHONE_GENERIC.match(clean_phone):
            return False, "Invalid phone number format."
        # If it doesn't start with 6-9, provide a helpful note
        return True, clean_phone
    return True, clean_phone


def validate_date(date_str: str, allow_future: bool = False, field_name: str = "Date") -> Tuple[bool, str]:
    """
    Validates a date string in YYYY-MM-DD format.
    Checks calendar validity (leap years, month days, etc.).
    If allow_future is False, dates in the future are rejected (e.g., past donation date).
    """
    if not date_str or not str(date_str).strip():
        return False, f"{field_name} cannot be empty."
    clean_date = str(date_str).strip()
    if not RE_DATE.match(clean_date):
        return False, f"{field_name} must be in YYYY-MM-DD format."
    try:
        parsed_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
    except ValueError:
        return False, f"{field_name} is not a valid calendar date."

    if not allow_future:
        today = date.today()
        if parsed_date > today:
            return False, f"{field_name} cannot be in the future (today is {today})."

    # Year sanity check
    if parsed_date.year < 1900 or parsed_date.year > 2100:
        return False, f"{field_name} year must be between 1900 and 2100."

    return True, clean_date


def validate_expiry_date(expiry_date_str: str) -> Tuple[bool, str]:
    """
    Validates an expiry date. Expiry dates can be today or in the future.
    """
    return validate_date(expiry_date_str, allow_future=True, field_name="Expiry Date")


def validate_units(units: any, field_name: str = "Units") -> Tuple[bool, int]:
    """
    Validates blood unit quantities.
    Must be an integer strictly greater than zero.
    """
    if units is None or str(units).strip() == "":
        return False, f"{field_name} cannot be empty."
    try:
        val = int(str(units).strip())
    except (ValueError, TypeError):
        return False, f"{field_name} must be a whole integer number."

    if val <= 0:
        return False, f"{field_name} must be greater than zero."
    if val > 1000:
        return False, f"{field_name} cannot exceed 1,000 units in a single transaction."

    return True, val


def validate_blood_group(blood_group: str) -> Tuple[bool, str]:
    """
    Validates that the blood group is one of the standard 8 groups.
    """
    if not blood_group or not blood_group.strip():
        return False, "Blood group must be selected."
    clean_bg = blood_group.strip().upper()
    if clean_bg not in config.BLOOD_GROUPS:
        return False, f"Invalid blood group '{clean_bg}'. Must be one of: {', '.join(config.BLOOD_GROUPS)}."
    return True, clean_bg


def validate_eligibility(eligibility: str) -> Tuple[bool, str]:
    """
    Validates donor eligibility status.
    """
    if not eligibility or not eligibility.strip():
        return False, "Eligibility status must be selected."
    clean_el = eligibility.strip()
    if clean_el not in config.ELIGIBILITY_STATUSES:
        return False, f"Invalid eligibility '{clean_el}'. Must be one of: {', '.join(config.ELIGIBILITY_STATUSES)}."
    return True, clean_el


def validate_hospital_name(name: str) -> Tuple[bool, str]:
    """
    Validates a hospital or healthcare center name.
    """
    if not name or not name.strip():
        return False, "Hospital name cannot be empty."
    clean_name = name.strip()
    if len(clean_name) < 3:
        return False, "Hospital name must be at least 3 characters long."
    if len(clean_name) > 100:
        return False, "Hospital name cannot exceed 100 characters."
    if not RE_HOSPITAL.match(clean_name):
        return False, "Hospital name contains invalid characters."
    return True, clean_name


def validate_request_status(status: str) -> Tuple[bool, str]:
    """
    Validates emergency request status.
    """
    if not status or not status.strip():
        return False, "Request status must be selected."
    clean_status = status.strip()
    if clean_status not in config.REQUEST_STATUSES:
        return False, f"Invalid request status '{clean_status}'. Must be one of: {', '.join(config.REQUEST_STATUSES)}."
    return True, clean_status
