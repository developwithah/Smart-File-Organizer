import customtkinter as ctk
from tkinter import messagebox

from organizer import organize_files
from config import *
from utils import select_folder, validate_folder


class SmartFileOrganizerApp:

    def __init__(self):

        self.app = ctk.CTk()

        self.app.title(APP_TITLE)
        self.app.geometry(WINDOW_SIZE)
        self.app.resizable(
            WINDOW_RESIZABLE,
            WINDOW_RESIZABLE
        )

        self.create_widgets()

    # ---------------------------------
    # UI
    # ---------------------------------

    def create_widgets(self):

        self.title = ctk.CTkLabel(
            self.app,
            text=APP_TITLE,
            font=TITLE_FONT
        )
        self.title.pack(pady=25)

        self.folder_entry = ctk.CTkEntry(
            self.app,
            width=500,
            placeholder_text="Select a folder..."
        )
        self.folder_entry.pack(pady=15)

        self.browse_button = ctk.CTkButton(
            self.app,
            text=BROWSE_BUTTON,
            command=self.browse_folder,
            width=180
        )
        self.browse_button.pack(pady=10)

        self.organize_button = ctk.CTkButton(
            self.app,
            text=ORGANIZE_BUTTON,
            command=self.run_organizer,
            width=180
        )
        self.organize_button.pack(pady=15)

        self.progress_bar = ctk.CTkProgressBar(
            self.app,
            width=500
        )
        self.progress_bar.pack(pady=20)
        self.progress_bar.set(PROGRESS_START)

        self.status_label = ctk.CTkLabel(
            self.app,
            text=STATUS_READY,
            font=STATUS_FONT
        )
        self.status_label.pack()

        self.counter_label = ctk.CTkLabel(
            self.app,
            text="Files Organized : 0",
            font=TEXT_FONT
        )
        self.counter_label.pack(pady=10)

    # ---------------------------------
    # Functions
    # ---------------------------------

    def browse_folder(self):

        folder = select_folder()

        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def update_progress(self, progress, count):

        self.progress_bar.set(progress)

        self.status_label.configure(
            text=f"Organizing... {int(progress*100)}%"
        )

        self.counter_label.configure(
            text=f"Files Organized : {count}"
        )

        self.app.update_idletasks()

    def run_organizer(self):

        folder = self.folder_entry.get().strip()

        if not validate_folder(folder):

            messagebox.showwarning(
                "Warning",
                "Please select a folder first."
            )
            return

        self.organize_button.configure(state="disabled")

        self.progress_bar.set(0)

        self.status_label.configure(
            text=STATUS_WORKING
        )

        self.counter_label.configure(
            text="Files Organized : 0"
        )

        self.app.update_idletasks()

        try:

            total = organize_files(
                folder,
                progress_callback=self.update_progress
            )

            self.progress_bar.set(PROGRESS_END)

            self.status_label.configure(
                text=STATUS_COMPLETE
            )

            self.counter_label.configure(
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

            self.status_label.configure(
                text="Status : Error"

            )

        finally:

            self.organize_button.configure(
                state="normal"
            )

    def run(self):
        self.app.mainloop()


def start_app():
    app = SmartFileOrganizerApp()
    app.run()