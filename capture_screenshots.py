"""
Automatic High-Resolution Screenshot Utility
Blood Bank Donor Directory & Stock Tracker (Branding: LIFELINE)
Student: Baire Gowda (25PG00157) - MCA 3rd Semester

Run this script on your Windows desktop to automatically navigate through
each redesigned application view and capture clean, genuine PNG screenshots into the screenshots/ directory.
Usage:
    python capture_screenshots.py
"""

import os
import sys
import time
from PIL import ImageGrab
import config
from main import BloodBankApp


def capture_all():
    print("=" * 70)
    print("  LIFELINE BLOOD BANK SYSTEM - AUTOMATED SCREENSHOT CAPTURE")
    print("=" * 70)
    print(f"Student: {config.STUDENT_NAME} ({config.STUDENT_ID}) - MCA 3rd Semester")
    print(f"Output Directory: {config.SCREENSHOTS_DIR}\n")

    os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)

    app = BloodBankApp()
    app.update()

    # Position window cleanly
    app.geometry("1320x820+40+30")
    app.update()

    views = [
        ("dashboard", "01_dashboard.png", "Overview & Analytics Dashboard"),
        ("donors",    "02_donor_directory.png", "Donor Directory & Registration"),
        ("stock",     "03_blood_inventory.png", "Blood Inventory & Donation Intake"),
        ("requests",  "04_hospital_requests.png", "Hospital Emergency Requisitions"),
        ("about",     "05_about_help.png", "About & Academic Workflow Guide"),
    ]

    for view_key, filename, description in views:
        print(f"Capturing: {description} -> {filename}...")
        app.show_view(view_key)
        app.update()
        time.sleep(1.2)  # Allow Tkinter to finish full visual repaint

        x = app.winfo_rootx()
        y = app.winfo_rooty()
        w = app.winfo_width()
        h = app.winfo_height()

        try:
            bbox = (x, y, x + w, y + h)
            screenshot = ImageGrab.grab(bbox=bbox)
            out_path = os.path.join(config.SCREENSHOTS_DIR, filename)
            screenshot.save(out_path)
            print(f"  [SAVED] {out_path} ({screenshot.size[0]}x{screenshot.size[1]} px)")
        except Exception as e:
            print(f"  [NOTE] Desktop display grab error: {e}")
            print("  Please run 'python capture_screenshots.py' directly on your active Windows desktop monitor.")
            break

    app.destroy()
    print("\nCapture process completed. Check your 'screenshots/' directory!")


if __name__ == "__main__":
    capture_all()
