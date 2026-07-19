"""
utils.py
Helper functions for Smart File Organizer
"""

from tkinter import filedialog


def select_folder():
    """
    Opens a folder selection dialog.

    Returns:
        str: Selected folder path or empty string.
    """
    folder = filedialog.askdirectory()

    if not folder:
        return ""

    return folder


def format_status(message):
    """
    Returns a formatted status message.
    """
    return f"Status: {message}"


def validate_folder(path):
    """
    Checks whether a folder has been selected.
    """
    return bool(path)