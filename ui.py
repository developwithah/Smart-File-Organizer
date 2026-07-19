import customtkinter as ctk
from tkinter import messagebox
import threading
import queue
import os

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_AND_DROP_AVAILABLE = True
except ImportError:
    DRAG_AND_DROP_AVAILABLE = False

from organizer import organize_files
from undo_manager import UndoManager
from config import *
from utils import select_folder, validate_folder


class SmartFileOrganizerApp:

    def __init__(self):

        self.app = ctk.CTk()
        self.event_queue = queue.Queue()
        self.undo_manager = UndoManager()
        self.worker_thread = None
        self.is_processing = False
        self.drag_and_drop_enabled = False

        self.app.title(APP_TITLE)
        self.app.geometry(WINDOW_SIZE)
        self.app.resizable(
            WINDOW_RESIZABLE,
            WINDOW_RESIZABLE
        )

        self.create_widgets()
        self.setup_drag_and_drop()

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

        self.drop_area = ctk.CTkLabel(
            self.app,
            text="Drag and drop a folder here",
            width=500,
            height=50,
            corner_radius=8,
            fg_color=("gray80", "gray25")
        )
        self.drop_area.pack(pady=(0, 10))

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

        self.undo_button = ctk.CTkButton(
            self.app,
            text=UNDO_BUTTON,
            command=self.run_undo,
            width=180,
            state="disabled"
        )
        self.undo_button.pack(pady=(0, 15))

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

    def setup_drag_and_drop(self):
        """Enable folder drops when tkinterdnd2 is installed."""
        if not DRAG_AND_DROP_AVAILABLE:
            self.show_drag_and_drop_unavailable()
            return

        try:
            TkinterDnD.require(self.app)
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind("<<DropEnter>>", self.on_drag_enter)
            self.drop_area.dnd_bind("<<DropLeave>>", self.on_drag_leave)
            self.drop_area.dnd_bind("<<Drop>>", self.handle_folder_drop)
            self.drag_and_drop_enabled = True

        except Exception:
            self.show_drag_and_drop_unavailable()

    def show_drag_and_drop_unavailable(self):
        """Keep the app usable and explain how to enable drag-and-drop."""
        self.drop_area.configure(
            text="Drag-and-drop unavailable — Browse still works"
        )
        self.app.after(
            100,
            lambda: messagebox.showinfo(
                "Drag-and-Drop Unavailable",
                "Drag-and-drop needs tkinterdnd2. Install project "
                "dependencies with:\npython -m pip install -r requirements.txt"
            )
        )

    def on_drag_enter(self, event):
        """Show that the dedicated drop area is ready to receive a folder."""
        self.drop_area.configure(text="Drop folder here...")

    def on_drag_leave(self, event):
        """Restore the idle message when a folder leaves the drop area."""
        if self.drag_and_drop_enabled:
            self.drop_area.configure(text="Drag and drop a folder here")

    def handle_folder_drop(self, event):
        """Validate a dropped path and use it as the selected folder."""
        dropped_paths = self.app.tk.splitlist(event.data)

        if len(dropped_paths) != 1:
            self.drop_area.configure(text="Please drop one folder at a time.")
            messagebox.showwarning(
                "Multiple Items Dropped",
                "Please drop one folder at a time."
            )
            return

        folder = dropped_paths[0]

        if not os.path.isdir(folder):
            self.drop_area.configure(
                text="Please drop a folder, not a file."
            )
            messagebox.showwarning(
                "Folder Required",
                "Please drop a folder, not a file."
            )
            return

        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, folder)
        self.drop_area.configure(text="Folder Ready")

    def browse_folder(self):

        folder = select_folder()

        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)

    def publish_event(self, event_type, payload=None):
        """Send a structured event from the worker to the GUI thread."""
        self.event_queue.put({
            "type": event_type,
            "payload": payload or {}
        })

    def queue_progress_update(self, progress, count):
        """Convert organizer progress callbacks into queue events."""
        self.publish_event(
            "progress",
            {
                "progress": progress,
                "count": count
            }
        )

    def queue_undo_progress_update(self, progress, restored, skipped):
        """Convert undo progress callbacks into queue events."""
        self.publish_event(
            "undo_progress",
            {
                "progress": progress,
                "restored": restored,
                "skipped": skipped
            }
        )

    def update_progress(self, progress, count):

        self.progress_bar.set(progress)

        self.status_label.configure(
            text=f"Organizing... {int(progress*100)}%"
        )

        self.counter_label.configure(
            text=f"Files Organized : {count}"
        )

        self.app.update_idletasks()

    def update_undo_progress(self, progress, restored, skipped):
        """Update the shared progress area while undo is in progress."""
        self.progress_bar.set(progress)
        self.status_label.configure(
            text=f"Undoing... {int(progress * 100)}%"
        )
        self.counter_label.configure(
            text=f"Files Restored : {restored} | Skipped : {skipped}"
        )
        self.app.update_idletasks()

    def organize_in_background(self, folder):
        """Run file organization without directly accessing UI widgets."""
        try:
            self.undo_manager.begin_operation()
            total = organize_files(
                folder,
                progress_callback=self.queue_progress_update,
                move_callback=self.undo_manager.record_move
            )
            undo_available = self.undo_manager.commit_operation()
            self.publish_event(
                "success",
                {"total": total, "undo_available": undo_available}
            )

        except Exception as error:
            self.undo_manager.discard_operation()
            self.publish_event("error", {"message": str(error)})

    def undo_in_background(self):
        """Restore the most recent operation without directly accessing UI."""
        try:
            result = self.undo_manager.undo_last_operation(
                progress_callback=self.queue_undo_progress_update
            )
            self.publish_event("undo_success", result)

        except Exception as error:
            self.publish_event("undo_error", {"message": str(error)})

    def process_queue(self):
        """Handle worker events on the main GUI thread."""
        try:
            while True:
                event = self.event_queue.get_nowait()
                event_type = event["type"]
                payload = event["payload"]

                if event_type == "progress":
                    self.update_progress(
                        payload["progress"],
                        payload["count"]
                    )

                elif event_type == "undo_progress":
                    self.update_undo_progress(
                        payload["progress"],
                        payload["restored"],
                        payload["skipped"]
                    )

                elif event_type == "success":
                    total = payload["total"]
                    self.progress_bar.set(PROGRESS_END)
                    self.status_label.configure(text=STATUS_COMPLETE)
                    self.counter_label.configure(
                        text=f"Files Organized : {total}"
                    )
                    messagebox.showinfo(
                        "Completed",
                        f"{total} file(s) organized successfully."
                    )
                    if payload["undo_available"]:
                        self.undo_button.configure(state="normal")
                    self.finish_processing()

                elif event_type == "error":
                    messagebox.showerror("Error", payload["message"])
                    self.status_label.configure(text="Status : Error")
                    if self.undo_manager.can_undo():
                        self.undo_button.configure(state="normal")
                    self.finish_processing()

                elif event_type == "undo_success":
                    self.handle_undo_success(payload)
                    self.finish_processing()

                elif event_type == "undo_error":
                    messagebox.showerror("Undo Error", payload["message"])
                    self.status_label.configure(text="Status : Undo Error")
                    if self.undo_manager.can_undo():
                        self.undo_button.configure(state="normal")
                    self.finish_processing()

                self.event_queue.task_done()

        except queue.Empty:
            pass

        if self.is_processing:
            self.app.after(100, self.process_queue)

    def finish_processing(self):
        """Restore controls after the worker reports completion or failure."""
        self.is_processing = False
        self.worker_thread = None
        self.organize_button.configure(state="normal")

    def handle_undo_success(self, result):
        """Show the outcome of an undo operation on the GUI thread."""
        self.progress_bar.set(PROGRESS_END)
        self.counter_label.configure(
            text=(
                f"Files Restored : {result['restored']} | "
                f"Skipped : {result['skipped']}"
            )
        )

        if result["completed"]:
            self.status_label.configure(text=STATUS_UNDO_COMPLETE)
            self.undo_button.configure(state="disabled")
            messagebox.showinfo(
                "Undo Completed",
                f"{result['restored']} file(s) restored successfully."
            )
        else:
            self.status_label.configure(text="Undo completed with skipped files.")
            self.undo_button.configure(state="normal")
            messagebox.showwarning(
                "Undo Partially Completed",
                (
                    f"Restored: {result['restored']}\n"
                    f"Skipped: {result['skipped']}\n\n"
                    "Resolve the skipped files and try undo again."
                )
            )

    def run_organizer(self):

        if self.is_processing:
            return

        folder = self.folder_entry.get().strip()

        if not validate_folder(folder):

            messagebox.showwarning(
                "Warning",
                "Please select a folder first."
            )
            return

        self.is_processing = True
        self.organize_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")

        self.progress_bar.set(0)

        self.status_label.configure(
            text=STATUS_WORKING
        )

        self.counter_label.configure(
            text="Files Organized : 0"
        )

        self.app.update_idletasks()

        self.worker_thread = threading.Thread(
            target=self.organize_in_background,
            args=(folder,)
        )
        self.worker_thread.start()
        self.app.after(100, self.process_queue)

    def run_undo(self):
        """Start undo in a background worker when a completed operation exists."""
        if self.is_processing or not self.undo_manager.can_undo():
            return

        self.is_processing = True
        self.organize_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")
        self.progress_bar.set(PROGRESS_START)
        self.status_label.configure(text=STATUS_UNDO_WORKING)
        self.counter_label.configure(text="Files Restored : 0 | Skipped : 0")
        self.app.update_idletasks()

        self.worker_thread = threading.Thread(target=self.undo_in_background)
        self.worker_thread.start()
        self.app.after(100, self.process_queue)

    def run(self):
        self.app.mainloop()


def start_app():
    app = SmartFileOrganizerApp()
    app.run()
