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
# NEW BRAND COLOUR SYSTEM (HEALTHCARE SAAS & SUPERDESIGN-INSPIRED)
# =============================================================================
PRIMARY_DARK_TEAL = "#0F3D3E"     # Deep dark teal (Sidebar, dark headers)
PRIMARY_TEAL      = "#0F766E"     # Primary brand actions, active highlights
ACCENT_MINT       = "#14B8A6"     # Accent mint, key focal points, badges
BACKGROUND        = "#F5F8F8"     # Modern minimal background (Superdesign style)
CARD_BACKGROUND   = "#FFFFFF"     # Crisp clean white cards and surfaces
MAIN_TEXT         = "#172B2A"     # High-contrast readable dark slate text
SECONDARY_TEXT    = "#64748B"     # Muted slate for subheaders, labels, helper text
BORDER            = "#E2E8F0"     # Soft subtle modern borders

# Semantic Status Accents
COLOR_SUCCESS     = "#16A34A"     # Green for successful operations / optimal stock
COLOR_WARNING     = "#D97706"     # Amber for warnings / low stock / pending
COLOR_DANGER      = "#DC4C4C"     # Medical red only for critical errors & emergency
COLOR_INFO        = "#2563EB"     # Blue for informational badges & approved status

# Selective Glass & Soft Tint Surfaces
TINT_MINT_LIGHT   = "#CCFBF1"     # Mint pill background
TINT_TEAL_LIGHT   = "#E6FFFA"     # Soft teal background
TINT_SUCCESS_LIGHT= "#DCFCE7"     # Green pill background
TINT_WARNING_LIGHT= "#FEF3C7"     # Amber pill background
TINT_DANGER_LIGHT = "#FEE2E2"     # Red pill background
TINT_INFO_LIGHT   = "#DBEAFE"     # Blue pill background

# Subtle Elevated Glassmorphic Tints
SURFACE_GLASS     = "#F8FAFC"     # Elevated frosted sub-card surface
SURFACE_MINT_GLASS= "#F0FDFA"     # Subtle mint glass surface
SURFACE_BLUE_GLASS= "#F0F9FF"     # Subtle blue glass surface
SURFACE_AMBER_GLASS= "#FFFBEB"    # Subtle amber glass surface
SURFACE_GREEN_GLASS= "#F0FDF4"    # Subtle green glass surface

# Interactive Hover & Active States
HOVER_TEAL        = "#0D655E"     # Primary button hover
HOVER_SIDEBAR     = "#154D4E"     # Sidebar item hover
ACTIVE_SIDEBAR    = "#0F766E"     # Sidebar active item
HOVER_DANGER      = "#B91C1C"     # Danger button hover
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
