import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox

from organizer import organize_files

# -----------------------------
# App Settings
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -----------------------------
# Functions
# -----------------------------
def browse_folder():
    folder = filedialog.askdirectory()

    if folder:
        folder_entry.delete(0, "end")
        folder_entry.insert(0, folder)


def run_organizer():
    folder = folder_entry.get().strip()

    if not folder:
        messagebox.showwarning(
            "No Folder Selected",
            "Please select a folder first."
        )
        return

    try:
        organize_files(folder)

        messagebox.showinfo(
            "Success",
            "Files organized successfully!"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )


# -----------------------------
# Main Window
# -----------------------------
app = ctk.CTk()

app.title("Smart File Organizer")
app.geometry("700x500")
app.resizable(False, False)


# -----------------------------
# Title
# -----------------------------
title = ctk.CTkLabel(
    app,
    text="Smart File Organizer",
    font=("Arial", 30, "bold")
)

title.pack(pady=40)


# -----------------------------
# Folder Entry
# -----------------------------
folder_entry = ctk.CTkEntry(
    app,
    width=500,
    placeholder_text="Select a folder..."
)

folder_entry.pack(pady=20)


# -----------------------------
# Browse Button
# -----------------------------
browse_button = ctk.CTkButton(
    app,
    text="Browse Folder",
    command=browse_folder,
    width=180
)

browse_button.pack(pady=10)


# -----------------------------
# Organize Button
# -----------------------------
organize_button = ctk.CTkButton(
    app,
    text="Organize Files",
    command=run_organizer,
    width=180
)

organize_button.pack(pady=20)


# -----------------------------
# Run App
# -----------------------------
app.mainloop()