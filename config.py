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
APP_VERSION = "2.8"

WINDOW_WIDTH = 980
WINDOW_HEIGHT = 760

WINDOW_MIN_WIDTH = 820
WINDOW_MIN_HEIGHT = 680

WINDOW_SIZE = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

WINDOW_RESIZABLE = True

# -----------------------------
# Layout and visual design
# -----------------------------
CONTENT_PADDING = 24
SECTION_SPACING = 16
CARD_SPACING = 12
BUTTON_WIDTH = 220
DROP_AREA_HEIGHT = 54
RESULTS_WINDOW_SIZE = "820x600"

HEADER_COLOR = ("#E8F1FF", "#1B2A41")
CARD_COLOR = ("#F7F9FC", "#1E293B")
DROP_AREA_COLOR = ("#EAF2FF", "#243B55")
STATUS_COLORS = {
    "ready": ("#16803C", "#4ADE80"),
    "processing": ("#B45309", "#FBBF24"),
    "storage": ("#1D4ED8", "#60A5FA"),
    "duplicates": ("#7E22CE", "#C084FC"),
    "error": ("#B91C1C", "#F87171")
}

# -----------------------------
# UI Text
# -----------------------------
BROWSE_BUTTON = "Browse Folder"

ORGANIZE_BUTTON = "Organize Files"

UNDO_BUTTON = "Undo Last Operation"

DUPLICATE_FINDER_BUTTON = "Find Duplicate Files"

STORAGE_ANALYZER_BUTTON = "Analyze Storage"

MENU_FILE = "File"
MENU_TOOLS = "Tools"
MENU_HELP = "Help"
MENU_OPEN_FOLDER = "Open Folder"
MENU_EXIT = "Exit"
MENU_ABOUT = "About"
MENU_VERSION_INFORMATION = "Version Information"

STATUS_READY = "Ready"

STATUS_WORKING = "Organizing files..."

STATUS_COMPLETE = "Completed successfully!"

STATUS_UNDO_WORKING = "Undoing last operation..."

STATUS_UNDO_COMPLETE = "Undo completed successfully!"

STATUS_DUPLICATE_WORKING = "Scanning for duplicate files..."

STATUS_STORAGE_WORKING = "Analyzing storage..."

STATUS_READY_TEXT = "Ready"
STATUS_PROCESSING_TEXT = "Processing"
STATUS_STORAGE_ANALYZED_TEXT = "Storage Analyzed"
STATUS_DUPLICATES_FOUND_TEXT = "Duplicates Found"
STATUS_ERROR_TEXT = "Error"

# -----------------------------
# Progress
# -----------------------------
PROGRESS_START = 0

PROGRESS_END = 1

# -----------------------------
# Fonts
# -----------------------------
TITLE_FONT = ("Segoe UI", 24, "bold")

SUBTITLE_FONT = ("Segoe UI", 13)

CARD_TITLE_FONT = ("Segoe UI", 12, "bold")

CARD_VALUE_FONT = ("Segoe UI", 16, "bold")

TEXT_FONT = ("Segoe UI", 14)

BUTTON_FONT = ("Segoe UI", 14, "bold")

STATUS_FONT = ("Segoe UI", 13)
