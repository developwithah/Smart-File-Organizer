"""
config.py
Application configuration
"""

import customtkinter as ctk

# -----------------------------
# Appearance
# -----------------------------
ctk.set_appearance_mode("System")      # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

# -----------------------------
# Window
# -----------------------------
APP_TITLE = "Smart File Organizer"

WINDOW_WIDTH = 750
WINDOW_HEIGHT = 600

WINDOW_SIZE = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

WINDOW_RESIZABLE = False

# -----------------------------
# UI Text
# -----------------------------
BROWSE_BUTTON = "Browse Folder"

ORGANIZE_BUTTON = "Organize Files"

UNDO_BUTTON = "Undo Last Operation"

DUPLICATE_FINDER_BUTTON = "Find Duplicate Files"

STORAGE_ANALYZER_BUTTON = "Analyze Storage"

STATUS_READY = "Ready"

STATUS_WORKING = "Organizing files..."

STATUS_COMPLETE = "Completed successfully!"

STATUS_UNDO_WORKING = "Undoing last operation..."

STATUS_UNDO_COMPLETE = "Undo completed successfully!"

STATUS_DUPLICATE_WORKING = "Scanning for duplicate files..."

STATUS_STORAGE_WORKING = "Analyzing storage..."

# -----------------------------
# Progress
# -----------------------------
PROGRESS_START = 0

PROGRESS_END = 1

# -----------------------------
# Fonts
# -----------------------------
TITLE_FONT = ("Segoe UI", 24, "bold")

TEXT_FONT = ("Segoe UI", 14)

BUTTON_FONT = ("Segoe UI", 14, "bold")

STATUS_FONT = ("Segoe UI", 13)
