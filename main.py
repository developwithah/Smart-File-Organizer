import customtkinter as ctk
from tkinter import filedialog, messagebox

from organizer import organize_files


# -----------------------------
# App Settings
# -----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -----------------------------
# Main Window
# -----------------------------
app = ctk.CTk()
app.title("Smart File Organizer")
app.geometry("700x500")
app.resizable(False, False)


# -----------------------------
# Functions
# -----------------------------
def browse_folder():
    folder = filedialog.askdirectory()

    if folder:
        folder_entry.delete(0, "end")
        folder_entry.insert(0, folder)


def update_progress(progress, count):

    progress_bar.set(progress)

    status_label.configure(
        text=f"Status : Organizing... {int(progress * 100)}%"
    )

    counter_label.configure(
        text=f"Files Organized : {count}"
    )

    app.update_idletasks()


def run_organizer():

    folder = folder_entry.get().strip()

    if not folder:
        messagebox.showwarning(
            "Warning",
            "Please select a folder first."
        )
        return

    organize_button.configure(state="disabled")

    progress_bar.set(0)

    status_label.configure(
        text="Status : Starting..."
    )

    counter_label.configure(
        text="Files Organized : 0"
    )

    app.update_idletasks()

    try:

        total = organize_files(
            folder,
            progress_callback=update_progress
        )

        progress_bar.set(1)

        status_label.configure(
            text="Status : Completed ✔️"
        )

        counter_label.configure(
            text=f"Files Organized : {total}"
        )

        messagebox.showinfo(
            "Completed",
            f"{total} file(s) organized successfully."
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            str(error)
        )

        status_label.configure(
            text="Status : Error"
        )

    finally:

        organize_button.configure(
            state="normal"
        )


# -----------------------------
# Title
# -----------------------------
title = ctk.CTkLabel(
    app,
    text="Smart File Organizer",
    font=("Arial", 28, "bold")
)

title.pack(pady=25)


# -----------------------------
# Folder Entry
# -----------------------------
folder_entry = ctk.CTkEntry(
    app,
    width=500,
    placeholder_text="Select a folder..."
)

folder_entry.pack(pady=15)


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

organize_button.pack(pady=15)


# -----------------------------
# Progress Bar
# -----------------------------
progress_bar = ctk.CTkProgressBar(
    app,
    width=500
)

progress_bar.pack(pady=20)

progress_bar.set(0)


# -----------------------------
# Status
# -----------------------------
status_label = ctk.CTkLabel(
    app,
    text="Status : Ready"
)

status_label.pack()


# -----------------------------
# Counter
# -----------------------------
counter_label = ctk.CTkLabel(
    app,
    text="Files Organized : 0"
)

counter_label.pack(pady=10)


# -----------------------------
# Run App
# -----------------------------
app.mainloop()