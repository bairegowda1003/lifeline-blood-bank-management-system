"""
Configuration and Centralized Design System Module
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Student: Baire Gowda (25PG00157) - MCA 3rd Semester
Healthcare SaaS-inspired Palette, Spacing, Typography, and Path Constants.
"""

import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "blood_bank.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DOCS_DIR = os.path.join(BASE_DIR, "documentation")

# Ensure required runtime folders exist
for folder in [DATABASE_DIR, ASSETS_DIR, SCREENSHOTS_DIR, DOCS_DIR]:
    os.makedirs(folder, exist_ok=True)

# Application Information & Branding
APP_BRAND = "LIFELINE"
APP_TITLE = "LIFELINE | Blood Bank Management System"
APP_SUBTITLE = "Blood Bank Management"
APP_VERSION = "3.0.0"
STUDENT_NAME = "Baire Gowda"
STUDENT_ID = "25PG00157"
COURSE = "MCA (Master of Computer Applications)"
SEMESTER = "3rd Semester"
ACADEMIC_YEAR = "2026-2027"

# =============================================================================
# NEW BRAND COLOUR SYSTEM (HEALTHCARE SAAS - NAVY, CYAN & MEDICAL RED)
# =============================================================================
COLOR_DARK_NAVY    = "#0B2545"     # Dark Navy: Master sidebar background, dark brand headers
COLOR_DEEP_NAVY    = "#102F50"     # Deep Navy: Sub-headers, active sidebar hover/container
COLOR_PRIMARY_CYAN = "#13B8CC"     # Primary Cyan: Key interactive accents, buttons, active highlights
COLOR_BRIGHT_TEAL  = "#16B8C5"     # Bright Teal: Vibrant focal points, badges, progress fills
COLOR_LIGHT_CYAN   = "#E0FAFC"     # Light Cyan: Subtle pill backgrounds, card headers, active tint
COLOR_WHITE        = "#FFFFFF"     # White: Cards, elevated surfaces, input backgrounds
COLOR_SOFT_BG      = "#F4F9FC"     # Soft Background: Application canvas
COLOR_SOFT_PINK    = "#FFF0F1"     # Soft Pink: Subtle emergency requisition backdrop
COLOR_MEDICAL_RED  = "#DC3545"     # Medical Red: Emergency actions, critical shortages, destructive
COLOR_SUCCESS      = "#16A34A"     # Success Green: Optimal stock, verified donors, fulfilled requests
COLOR_WARNING      = "#D97706"     # Warning Amber: Low-stock notices, pending hospital requests
COLOR_MAIN_TEXT    = "#142D45"     # Main Text: High-contrast readable deep navy slate text
COLOR_SECONDARY_TEXT = "#64748B"   # Secondary Text: Muted slate for subheaders, labels, helper text
COLOR_BORDER       = "#E2E8F0"     # Border: Soft subtle modern borders

# Canonical Palette Constants
DARK_NAVY       = COLOR_DARK_NAVY
DEEP_NAVY       = COLOR_DEEP_NAVY
PRIMARY_CYAN    = COLOR_PRIMARY_CYAN
BRIGHT_TEAL     = COLOR_BRIGHT_TEAL
LIGHT_CYAN      = COLOR_LIGHT_CYAN
BACKGROUND      = COLOR_SOFT_BG
CARD_BACKGROUND = COLOR_WHITE
SOFT_PINK       = COLOR_SOFT_PINK
MEDICAL_RED     = COLOR_MEDICAL_RED
MAIN_TEXT       = COLOR_MAIN_TEXT
SECONDARY_TEXT  = COLOR_SECONDARY_TEXT
BORDER          = COLOR_BORDER

# Semantic Presets & Brand Anchors
PRIMARY_DARK_TEAL = COLOR_DARK_NAVY
PRIMARY_TEAL      = COLOR_PRIMARY_CYAN
ACCENT_MINT       = COLOR_BRIGHT_TEAL
COLOR_DANGER      = COLOR_MEDICAL_RED
COLOR_INFO        = COLOR_PRIMARY_CYAN

# Soft Tint Surfaces & Badges
TINT_CYAN_LIGHT   = COLOR_LIGHT_CYAN
TINT_MINT_LIGHT   = COLOR_LIGHT_CYAN
TINT_TEAL_LIGHT   = COLOR_LIGHT_CYAN
TINT_SUCCESS_LIGHT= "#DCFCE7"     # Green pill background
TINT_WARNING_LIGHT= "#FEF3C7"     # Amber pill background
TINT_DANGER_LIGHT = COLOR_SOFT_PINK # Soft pink for danger/emergency pill background
TINT_INFO_LIGHT   = "#E0F2FE"     # Sky/Cyan light pill background

# Subtle Elevated Glassmorphic Tints
SURFACE_GLASS      = "#F8FAFC"     # Elevated frosted sub-card surface
SURFACE_MINT_GLASS = COLOR_LIGHT_CYAN
SURFACE_BLUE_GLASS = "#F0F9FF"
SURFACE_AMBER_GLASS= "#FFFBEB"
SURFACE_GREEN_GLASS= "#F0FDF4"
SURFACE_PINK_GLASS = COLOR_SOFT_PINK

# Interactive Hover & Active States
HOVER_CYAN        = "#0EA5B8"     # Cyan button hover
HOVER_TEAL        = COLOR_PRIMARY_CYAN
HOVER_SIDEBAR     = COLOR_DEEP_NAVY
ACTIVE_SIDEBAR    = COLOR_PRIMARY_CYAN
HOVER_DANGER      = "#B02A37"     # Medical red hover
HOVER_SECONDARY   = "#E2E8F0"     # Light button hover

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES (Ensures 100% existing code compatibility)
# =============================================================================
COLOR_NAVY_DARK    = PRIMARY_DARK_TEAL
COLOR_NAVY_MEDIUM  = HOVER_SIDEBAR
COLOR_NAVY_LIGHT   = ACTIVE_SIDEBAR
COLOR_BG_LIGHT     = BACKGROUND
COLOR_CARD_BG      = CARD_BACKGROUND
COLOR_CARD_BORDER  = BORDER
COLOR_TEXT_MAIN    = MAIN_TEXT
COLOR_TEXT_MUTED   = SECONDARY_TEXT
COLOR_TEXT_LIGHT   = "#FFFFFF"
COLOR_RED_PRIMARY  = COLOR_DANGER
COLOR_RED_HOVER    = HOVER_DANGER
COLOR_RED_LIGHT    = TINT_DANGER_LIGHT
COLOR_GREEN_SUCCESS= COLOR_SUCCESS
COLOR_GREEN_LIGHT  = TINT_SUCCESS_LIGHT
COLOR_AMBER_WARN   = COLOR_WARNING
COLOR_AMBER_LIGHT  = TINT_WARNING_LIGHT
COLOR_BLUE_INFO    = COLOR_INFO
COLOR_BLUE_LIGHT   = TINT_INFO_LIGHT

# Blood Groups Specification
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
BLOOD_TYPES = ["A", "B", "AB", "O"]
RH_FACTORS = ["Positive (+)", "Negative (-)"]
RH_MAP = {
    "Positive (+)": "+",
    "Negative (-)": "-",
    "+": "Positive (+)",
    "-": "Negative (-)"
}

# Donor Eligibility Constants
ELIGIBILITY_STATUSES = [
    "Eligible",
    "Not Eligible",
    "Pending Verification"
]

# Request Status Constants
REQUEST_STATUSES = [
    "Pending",
    "Approved",
    "Rejected",
    "Fulfilled"
]

# Stock Thresholds
LOW_STOCK_THRESHOLD = 5          # Units below this are marked Low Stock
CRITICAL_STOCK_THRESHOLD = 2     # Units below this are Critical
SHELF_LIFE_DAYS = 42             # Standard red blood cell storage life (approx 35-42 days)
EXPIRY_WARN_DAYS = 7             # Warn if stock expires within 7 days

# Modern Typography Scale (Segoe UI)
FONT_HERO        = ("Segoe UI", 18, "bold")
FONT_TITLE       = ("Segoe UI", 15, "bold")
FONT_HEADER      = ("Segoe UI", 13, "bold")
FONT_SUBHEADER   = ("Segoe UI", 11, "bold")
FONT_REGULAR     = ("Segoe UI", 10)
FONT_BOLD        = ("Segoe UI", 10, "bold")
FONT_SMALL       = ("Segoe UI", 9)
FONT_SMALL_BOLD  = ("Segoe UI", 9, "bold")
FONT_TINY        = ("Segoe UI", 8)
FONT_CARD_VALUE  = ("Segoe UI", 24, "bold")
