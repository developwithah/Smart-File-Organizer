import customtkinter as ctk
from tkinter import Menu, messagebox
import os
import platform
import queue
import threading

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_AND_DROP_AVAILABLE = True
except ImportError:
    DRAG_AND_DROP_AVAILABLE = False

from config import *
from duplicate_finder import find_duplicate_files
from organizer import organize_files
from storage_analyzer import analyze_storage
from undo_manager import UndoManager
from utils import select_folder, validate_folder


class SmartFileOrganizerApp:
    """Coordinate the UI while keeping file operations in dedicated modules."""

    def __init__(self):
        self.app = ctk.CTk()
        self.event_queue = queue.Queue()
        self.undo_manager = UndoManager()
        self.worker_thread = None
        self.is_processing = False
        self.drag_and_drop_enabled = False

        self.dashboard_folder_var = ctk.StringVar(value=EMPTY_DASHBOARD_FOLDER)
        self.dashboard_files_var = ctk.StringVar(value="Not analyzed")
        self.dashboard_size_var = ctk.StringVar(value="Not analyzed")
        self.dashboard_duplicates_var = ctk.StringVar(value="Not scanned")
        self.dashboard_status_var = ctk.StringVar(value=f"● {STATUS_READY_TEXT}")
        self.bottom_status_var = ctk.StringVar(value=STATUS_READY_TEXT)

        self.app.title(APP_TITLE)
        self.app.geometry(WINDOW_SIZE)
        self.app.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.app.resizable(WINDOW_RESIZABLE, WINDOW_RESIZABLE)
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(3, weight=1)

        self.create_menu_bar()
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        self.configure_application_icon()
        self.setup_drag_and_drop()
        self.set_status(STATUS_READY_TEXT, "ready")
        self.sync_action_states()

    # ---------------------------------
    # Layout
    # ---------------------------------

    def create_menu_bar(self):
        """Create familiar application menus that call existing actions."""
        self.menu_bar = Menu(self.app)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.tools_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu = Menu(self.menu_bar, tearoff=0)

        self.file_menu.add_command(
            label=MENU_OPEN_FOLDER,
            command=self.browse_folder,
            accelerator="Ctrl+O"
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label=MENU_EXIT, command=self.exit_app)

        self.tools_menu.add_command(
            label=ORGANIZE_BUTTON,
            command=self.run_organizer
        )
        self.tools_menu.add_command(
            label=UNDO_BUTTON,
            command=self.run_undo,
            accelerator="Ctrl+Z"
        )
        self.tools_menu.add_command(
            label=DUPLICATE_FINDER_BUTTON,
            command=self.run_duplicate_finder,
            accelerator="Ctrl+D"
        )
        self.tools_menu.add_command(
            label=STORAGE_ANALYZER_BUTTON,
            command=self.run_storage_analyzer,
            accelerator="Ctrl+S"
        )

        self.help_menu.add_command(
            label=MENU_ABOUT,
            command=self.show_about_dialog,
            accelerator="F1"
        )
        self.help_menu.add_command(
            label=MENU_VERSION_INFORMATION,
            command=self.show_version_information
        )

        self.menu_bar.add_cascade(label=MENU_FILE, menu=self.file_menu)
        self.menu_bar.add_cascade(label=MENU_TOOLS, menu=self.tools_menu)
        self.menu_bar.add_cascade(label=MENU_HELP, menu=self.help_menu)
        self.app.configure(menu=self.menu_bar)

    def create_widgets(self):
        """Build the responsive grid layout and its reusable UI sections."""
        self.create_toolbar()

        header = ctk.CTkFrame(self.app, fg_color=HEADER_COLOR)
        header.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=CONTENT_PADDING,
            pady=(CONTENT_PADDING, SECTION_SPACING)
        )
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=APP_TITLE, font=TITLE_FONT).grid(
            row=0, column=0, padx=CONTENT_PADDING, pady=(18, 2)
        )
        ctk.CTkLabel(
            header,
            text="Organize, analyze, and understand your files.",
            font=SUBTITLE_FONT
        ).grid(row=1, column=0, padx=CONTENT_PADDING, pady=(0, 18))

        self.create_folder_panel()
        self.create_dashboard()
        self.create_progress_panel()
        self.create_status_bar()

    def create_toolbar(self):
        """Create the primary, icon-labeled action surface below the menu."""
        toolbar = ctk.CTkFrame(self.app, fg_color=TOOLBAR_COLOR)
        toolbar.grid(row=0, column=0, sticky="ew", padx=CONTENT_PADDING, pady=(8, 8))
        for column in range(5):
            toolbar.grid_columnconfigure(column, weight=1, uniform="toolbar")

        self.browse_button = self.create_toolbar_button(
            toolbar, TOOLBAR_BROWSE_BUTTON, self.browse_folder, 0
        )
        self.organize_button = self.create_toolbar_button(
            toolbar, TOOLBAR_ORGANIZE_BUTTON, self.run_organizer, 1
        )
        self.undo_button = self.create_toolbar_button(
            toolbar, TOOLBAR_UNDO_BUTTON, self.run_undo, 2
        )
        self.find_duplicates_button = self.create_toolbar_button(
            toolbar, TOOLBAR_DUPLICATE_BUTTON, self.run_duplicate_finder, 3
        )
        self.analyze_storage_button = self.create_toolbar_button(
            toolbar, TOOLBAR_STORAGE_BUTTON, self.run_storage_analyzer, 4
        )

    def create_toolbar_button(self, parent, text, command, column):
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=TOOLBAR_BUTTON_WIDTH,
            font=BUTTON_FONT
        )
        button.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=8,
            pady=8
        )
        return button

    def create_folder_panel(self):
        folder_panel = ctk.CTkFrame(self.app)
        folder_panel.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=CONTENT_PADDING,
            pady=(0, SECTION_SPACING)
        )
        folder_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            folder_panel,
            text="Folder Selection",
            font=CARD_TITLE_FONT
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 6))

        self.folder_entry = ctk.CTkEntry(
            folder_panel,
            placeholder_text=EMPTY_FOLDER_MESSAGE
        )
        self.folder_entry.grid(row=1, column=0, sticky="ew", padx=16, pady=6)
        self.folder_entry.bind("<KeyRelease>", self.on_folder_entry_changed)

        self.drop_area = ctk.CTkLabel(
            folder_panel,
            text=EMPTY_DROP_MESSAGE,
            height=DROP_AREA_HEIGHT,
            corner_radius=8,
            fg_color=DROP_AREA_COLOR
        )
        self.drop_area.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=16,
            pady=(6, 14)
        )

    def create_dashboard(self):
        dashboard = ctk.CTkFrame(self.app)
        dashboard.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=CONTENT_PADDING,
            pady=(0, SECTION_SPACING)
        )
        for column in range(3):
            dashboard.grid_columnconfigure(column, weight=1, uniform="dashboard")

        ctk.CTkLabel(
            dashboard,
            text="Dashboard",
            font=CARD_TITLE_FONT
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 6))

        self.create_dashboard_card(
            dashboard, "Selected Folder", self.dashboard_folder_var, 1, 0, 3
        )
        self.create_dashboard_card(
            dashboard, "Total Files", self.dashboard_files_var, 2, 0
        )
        self.create_dashboard_card(
            dashboard, "Total Size", self.dashboard_size_var, 2, 1
        )
        self.create_dashboard_card(
            dashboard, "Duplicate Groups", self.dashboard_duplicates_var, 2, 2
        )
        self.status_card = self.create_dashboard_card(
            dashboard, "Current Status", self.dashboard_status_var, 3, 0, 3
        )
        self.status_value_label.configure(text_color=STATUS_COLORS["ready"])

    def create_dashboard_card(self, parent, title, value, row, column, columnspan=1):
        card = ctk.CTkFrame(parent, fg_color=CARD_COLOR)
        card.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="nsew",
            padx=CARD_SPACING,
            pady=CARD_SPACING
        )
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=title, font=CARD_TITLE_FONT).grid(
            row=0, column=0, sticky="w", padx=14, pady=(10, 2)
        )
        value_label = ctk.CTkLabel(
            card,
            textvariable=value,
            font=CARD_VALUE_FONT,
            anchor="w"
        )
        value_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

        if title == "Current Status":
            self.status_value_label = value_label

        return card

    def create_progress_panel(self):
        progress_panel = ctk.CTkFrame(self.app)
        progress_panel.grid(
            row=4,
            column=0,
            sticky="new",
            padx=CONTENT_PADDING,
            pady=(0, CONTENT_PADDING)
        )
        progress_panel.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(progress_panel)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        self.progress_bar.set(PROGRESS_START)

        self.status_label = ctk.CTkLabel(
            progress_panel,
            text=STATUS_READY,
            font=STATUS_FONT
        )
        self.status_label.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 2))

        self.counter_label = ctk.CTkLabel(
            progress_panel,
            text="Files Organized : 0",
            font=TEXT_FONT
        )
        self.counter_label.grid(row=2, column=0, sticky="w", padx=16, pady=(0, 14))

    def create_status_bar(self):
        """Create a persistent status bar with the current app version."""
        status_bar = ctk.CTkFrame(
            self.app,
            height=STATUS_BAR_HEIGHT,
            fg_color=STATUS_BAR_COLOR
        )
        status_bar.grid(row=5, column=0, sticky="ew")
        status_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            status_bar,
            textvariable=self.bottom_status_var,
            font=STATUS_FONT,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=CONTENT_PADDING, pady=6)
        ctk.CTkLabel(
            status_bar,
            text=f"{APP_TITLE} v{APP_VERSION}",
            font=STATUS_FONT,
            anchor="e"
        ).grid(row=0, column=1, sticky="e", padx=CONTENT_PADDING, pady=6)

    # ---------------------------------
    # Menu, shortcuts, and UI state
    # ---------------------------------

    def setup_keyboard_shortcuts(self):
        self.app.bind_all("<Control-o>", self.handle_shortcut(self.browse_folder))
        self.app.bind_all("<Control-d>", self.handle_shortcut(self.run_duplicate_finder))
        self.app.bind_all("<Control-s>", self.handle_shortcut(self.run_storage_analyzer))
        self.app.bind_all("<Control-z>", self.handle_shortcut(self.run_undo))
        self.app.bind_all("<F1>", self.handle_shortcut(self.show_about_dialog))

    @staticmethod
    def handle_shortcut(command):
        def callback(event):
            command()
            return "break"

        return callback

    def set_status(self, message, indicator="ready"):
        """Synchronize the visible status label and dashboard status card."""
        indicator_text = {
            "ready": STATUS_READY_TEXT,
            "processing": STATUS_PROCESSING_TEXT,
            "storage": STATUS_STORAGE_ANALYZED_TEXT,
            "duplicates": STATUS_DUPLICATES_FOUND_TEXT,
            "error": STATUS_ERROR_TEXT
        }[indicator]
        self.status_label.configure(text=message)
        self.bottom_status_var.set(f"Status: {message}")
        self.dashboard_status_var.set(f"● {indicator_text}")
        self.status_value_label.configure(text_color=STATUS_COLORS[indicator])

    def set_selected_folder(self, folder):
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, folder)
        self.dashboard_folder_var.set(folder)
        self.dashboard_files_var.set("Not analyzed")
        self.dashboard_size_var.set("Not analyzed")
        self.dashboard_duplicates_var.set("Not scanned")
        self.sync_action_states()

    def on_folder_entry_changed(self, event):
        """Keep the empty state and action availability correct for typed paths."""
        folder = self.folder_entry.get().strip()
        self.dashboard_folder_var.set(folder or EMPTY_DASHBOARD_FOLDER)
        self.dashboard_files_var.set("Not analyzed")
        self.dashboard_size_var.set("Not analyzed")
        self.dashboard_duplicates_var.set("Not scanned")
        self.sync_action_states()

    def sync_action_states(self):
        """Keep buttons and menu commands aligned with the current app state."""
        folder_is_selected = bool(self.folder_entry.get().strip())
        normal_or_disabled = "disabled" if self.is_processing else "normal"
        folder_action_state = (
            "normal" if folder_is_selected and not self.is_processing else "disabled"
        )
        undo_state = (
            "normal"
            if not self.is_processing and self.undo_manager.can_undo()
            else "disabled"
        )

        self.browse_button.configure(state=normal_or_disabled)
        self.organize_button.configure(state=folder_action_state)
        self.find_duplicates_button.configure(state=folder_action_state)
        self.analyze_storage_button.configure(state=folder_action_state)
        self.undo_button.configure(state=undo_state)

        self.file_menu.entryconfigure(MENU_OPEN_FOLDER, state=normal_or_disabled)
        self.tools_menu.entryconfigure(ORGANIZE_BUTTON, state=folder_action_state)
        self.tools_menu.entryconfigure(UNDO_BUTTON, state=undo_state)
        self.tools_menu.entryconfigure(DUPLICATE_FINDER_BUTTON, state=folder_action_state)
        self.tools_menu.entryconfigure(STORAGE_ANALYZER_BUTTON, state=folder_action_state)

    def configure_application_icon(self):
        """Apply a future optional icon without requiring an asset today."""
        if not APP_ICON_PATH or not os.path.isfile(APP_ICON_PATH):
            return

        try:
            self.app.iconbitmap(APP_ICON_PATH)
        except Exception:
            pass

    def exit_app(self):
        if self.is_processing:
            should_exit = messagebox.askyesno(
                "Operation in Progress",
                "A file operation is still running. Exit the application?"
            )
            if not should_exit:
                return
        self.app.destroy()

    def show_about_dialog(self):
        about_window = ctk.CTkToplevel(self.app)
        about_window.title(MENU_ABOUT)
        about_window.geometry("480x390")
        about_window.resizable(False, False)
        about_window.transient(self.app)

        about_text = (
            f"{APP_TITLE}\n"
            f"Version {APP_VERSION}\n\n"
            f"Python: {platform.python_version()}\n"
            f"CustomTkinter: {ctk.__version__}\n\n"
            "Features\n"
            "• File organization by type\n"
            "• Responsive background processing\n"
            "• Folder drag and drop\n"
            "• Undo last operation\n"
            "• Duplicate file finder\n"
            "• Storage analyzer"
        )
        ctk.CTkLabel(
            about_window,
            text=about_text,
            justify="left",
            font=TEXT_FONT
        ).pack(padx=28, pady=28, anchor="w")

    def show_version_information(self):
        messagebox.showinfo(
            MENU_VERSION_INFORMATION,
            (
                f"{APP_TITLE} {APP_VERSION}\n"
                f"Python {platform.python_version()}\n"
                f"CustomTkinter {ctk.__version__}"
            )
        )

    # ---------------------------------
    # Folder selection and drag/drop
    # ---------------------------------

    def setup_drag_and_drop(self):
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
        self.drop_area.configure(text="Drag-and-drop unavailable - Browse still works")
        self.app.after(
            100,
            lambda: messagebox.showinfo(
                "Drag-and-Drop Unavailable",
                "Drag-and-drop needs tkinterdnd2. Install dependencies with:\n"
                "python -m pip install -r requirements.txt"
            )
        )

    def on_drag_enter(self, event):
        if not self.is_processing:
            self.drop_area.configure(text="Drop folder here...")

    def on_drag_leave(self, event):
        if self.drag_and_drop_enabled and not self.is_processing:
            self.drop_area.configure(text="Drag and drop a folder here")

    def handle_folder_drop(self, event):
        if self.is_processing:
            return

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
            self.drop_area.configure(text="Please drop a folder, not a file.")
            messagebox.showwarning(
                "Folder Required",
                "Please drop a folder, not a file."
            )
            return

        self.set_selected_folder(folder)
        self.drop_area.configure(text="Folder Ready")
        self.set_status("Folder ready for an action.", "ready")

    def browse_folder(self):
        if self.is_processing:
            return

        folder = select_folder()
        if folder:
            self.set_selected_folder(folder)
            self.drop_area.configure(text="Folder Ready")
            self.set_status("Folder ready for an action.", "ready")

    # ---------------------------------
    # Thread-safe event handling
    # ---------------------------------

    def publish_event(self, event_type, payload=None):
        self.event_queue.put({"type": event_type, "payload": payload or {}})

    def queue_progress_update(self, progress, count):
        self.publish_event("progress", {"progress": progress, "count": count})

    def queue_undo_progress_update(self, progress, restored, skipped):
        self.publish_event(
            "undo_progress",
            {"progress": progress, "restored": restored, "skipped": skipped}
        )

    def queue_duplicate_progress_update(
        self, phase, processed, total, group_count, duplicate_count
    ):
        self.publish_event(
            "duplicate_progress",
            {
                "phase": phase,
                "processed": processed,
                "total": total,
                "group_count": group_count,
                "duplicate_count": duplicate_count
            }
        )

    def queue_storage_progress_update(self, phase, processed, total, total_size):
        self.publish_event(
            "storage_progress",
            {
                "phase": phase,
                "processed": processed,
                "total": total,
                "total_size": total_size
            }
        )

    def update_progress(self, progress, count):
        self.progress_bar.set(progress)
        self.set_status(f"Organizing files... {int(progress * 100)}%", "processing")
        self.counter_label.configure(text=f"Files Organized : {count}")
        self.app.update_idletasks()

    def update_undo_progress(self, progress, restored, skipped):
        self.progress_bar.set(progress)
        self.set_status(f"Undoing... {int(progress * 100)}%", "processing")
        self.counter_label.configure(
            text=f"Files Restored : {restored} | Skipped : {skipped}"
        )
        self.app.update_idletasks()

    def update_duplicate_progress(self, payload):
        total = payload["total"]
        processed = payload["processed"]
        if payload["phase"] == "collecting":
            self.set_status("Finding files to scan...", "processing")
            self.counter_label.configure(text="Preparing duplicate scan...")
            return

        progress = processed / total if total else PROGRESS_END
        self.progress_bar.set(progress)
        self.set_status(
            f"Scanning for duplicates... {int(progress * 100)}%", "processing"
        )
        self.counter_label.configure(text=f"Files Hashed : {processed} / {total}")
        self.app.update_idletasks()

    def update_storage_progress(self, payload):
        if payload["phase"] == "collecting":
            self.set_status("Finding files to analyze...", "processing")
            self.counter_label.configure(text="Preparing storage analysis...")
            return

        total = payload["total"]
        processed = payload["processed"]
        progress = processed / total if total else PROGRESS_END
        self.progress_bar.set(progress)
        self.set_status(
            f"Analyzing storage... {int(progress * 100)}%", "processing"
        )
        self.counter_label.configure(
            text=(
                f"Files Analyzed : {processed} / {total} | "
                f"Size : {self.format_file_size(payload['total_size'])}"
            )
        )
        self.app.update_idletasks()

    # ---------------------------------
    # Background operations
    # ---------------------------------

    def organize_in_background(self, folder):
        try:
            self.undo_manager.begin_operation()
            total = organize_files(
                folder,
                progress_callback=self.queue_progress_update,
                move_callback=self.undo_manager.record_move
            )
            self.publish_event(
                "success",
                {
                    "total": total,
                    "undo_available": self.undo_manager.commit_operation()
                }
            )
        except Exception as error:
            self.undo_manager.discard_operation()
            self.publish_event("error", {"message": str(error)})

    def undo_in_background(self):
        try:
            result = self.undo_manager.undo_last_operation(
                progress_callback=self.queue_undo_progress_update
            )
            self.publish_event("undo_success", result)
        except Exception as error:
            self.publish_event("undo_error", {"message": str(error)})

    def find_duplicates_in_background(self, folder):
        try:
            result = find_duplicate_files(
                folder,
                progress_callback=self.queue_duplicate_progress_update
            )
            self.publish_event("duplicate_success", {"result": result})
        except Exception as error:
            self.publish_event("duplicate_error", {"message": str(error)})

    def analyze_storage_in_background(self, folder):
        try:
            result = analyze_storage(
                folder,
                progress_callback=self.queue_storage_progress_update
            )
            self.publish_event("storage_success", {"result": result})
        except Exception as error:
            self.publish_event("storage_error", {"message": str(error)})

    def process_queue(self):
        try:
            while True:
                event = self.event_queue.get_nowait()
                self.handle_event(event["type"], event["payload"])
                self.event_queue.task_done()
        except queue.Empty:
            pass

        if self.is_processing:
            self.app.after(100, self.process_queue)

    def handle_event(self, event_type, payload):
        if event_type == "progress":
            self.update_progress(payload["progress"], payload["count"])
        elif event_type == "undo_progress":
            self.update_undo_progress(
                payload["progress"], payload["restored"], payload["skipped"]
            )
        elif event_type == "duplicate_progress":
            self.update_duplicate_progress(payload)
        elif event_type == "storage_progress":
            self.update_storage_progress(payload)
        elif event_type == "success":
            self.handle_organize_success(payload)
        elif event_type == "error":
            self.handle_error("Error", payload["message"])
        elif event_type == "undo_success":
            self.handle_undo_success(payload)
        elif event_type == "undo_error":
            self.handle_error("Undo Error", payload["message"])
        elif event_type == "duplicate_success":
            self.handle_duplicate_success(payload["result"])
        elif event_type == "duplicate_error":
            self.handle_error("Duplicate Scan Error", payload["message"])
        elif event_type == "storage_success":
            self.handle_storage_success(payload["result"])
        elif event_type == "storage_error":
            self.handle_error("Storage Analysis Error", payload["message"])

    def finish_processing(self):
        self.is_processing = False
        self.worker_thread = None
        self.sync_action_states()

    def handle_organize_success(self, payload):
        total = payload["total"]
        self.progress_bar.set(PROGRESS_END)
        self.set_status(f"Completed successfully: {total} file(s) organized.", "ready")
        self.counter_label.configure(text=f"Files Organized : {total}")
        messagebox.showinfo("Completed", f"{total} file(s) organized successfully.")
        self.finish_processing()

    def handle_error(self, title, message):
        messagebox.showerror(title, message)
        self.set_status(f"{STATUS_ERROR_TEXT}: {message}", "error")
        self.finish_processing()

    def handle_undo_success(self, result):
        self.progress_bar.set(PROGRESS_END)
        self.counter_label.configure(
            text=(
                f"Files Restored : {result['restored']} | "
                f"Skipped : {result['skipped']}"
            )
        )
        if result["completed"]:
            self.set_status(STATUS_UNDO_COMPLETE, "ready")
            messagebox.showinfo(
                "Undo Completed",
                f"{result['restored']} file(s) restored successfully."
            )
        else:
            self.set_status("Undo completed with skipped files.", "error")
            messagebox.showwarning(
                "Undo Partially Completed",
                (
                    f"Restored: {result['restored']}\n"
                    f"Skipped: {result['skipped']}\n\n"
                    "Resolve the skipped files and try undo again."
                )
            )
        self.finish_processing()

    def handle_duplicate_success(self, result):
        self.progress_bar.set(PROGRESS_END)
        group_count = len(result.groups)
        self.dashboard_duplicates_var.set(str(group_count))
        self.counter_label.configure(text=f"Duplicate Groups : {group_count}")

        if result.groups:
            self.set_status(f"{group_count} duplicate group(s) found.", "duplicates")
            self.show_duplicate_results(result)
        else:
            self.set_status("No duplicate files were found.", "ready")
            messagebox.showinfo("Duplicate Scan Completed", "No duplicate files were found.")
        self.finish_processing()

    def handle_storage_success(self, result):
        self.progress_bar.set(PROGRESS_END)
        self.dashboard_files_var.set(str(result.total_files))
        self.dashboard_size_var.set(self.format_file_size(result.total_size))
        self.counter_label.configure(
            text=f"Total Storage : {self.format_file_size(result.total_size)}"
        )
        self.set_status("Storage analysis completed.", "storage")
        self.show_storage_results(result)
        self.finish_processing()

    # ---------------------------------
    # Read-only result dialogs
    # ---------------------------------

    def show_duplicate_results(self, result):
        results_window, results_text = self.create_results_window(
            "Duplicate File Results"
        )
        duplicate_files = sum(len(group.file_paths) for group in result.groups)
        wasted_space = sum(group.wasted_space for group in result.groups)
        results_text.insert(
            "end",
            (
                f"Duplicate groups: {len(result.groups)}\n"
                f"Duplicate files: {duplicate_files}\n"
                f"Potential recoverable space: {self.format_file_size(wasted_space)}\n\n"
            )
        )

        for index, group in enumerate(result.groups, start=1):
            results_text.insert(
                "end",
                (
                    f"Group {index} - {len(group.file_paths)} files\n"
                    f"SHA-256: {group.file_hash}\n"
                    f"File size: {self.format_file_size(group.file_size)}\n"
                    f"Potential recoverable space: "
                    f"{self.format_file_size(group.wasted_space)}\n"
                )
            )
            for file_path in group.file_paths:
                results_text.insert("end", f"  - {file_path}\n")
            results_text.insert("end", "\n")

        results_text.configure(state="disabled")
        results_window.focus()

    def show_storage_results(self, result):
        results_window, results_text = self.create_results_window("Storage Analysis")
        results_text.insert("end", "Storage Analysis\n\n")
        results_text.insert("end", f"Total files: {result.total_files}\n")
        results_text.insert("end", f"Total folders: {result.total_folders}\n")
        results_text.insert(
            "end", f"Total size: {self.format_file_size(result.total_size)}\n"
        )
        results_text.insert("end", f"Skipped files: {result.skipped_files}\n\n")

        results_text.insert("end", "Storage by Category\n")
        for category in result.categories:
            percentage = (
                category.total_size / result.total_size * 100
                if result.total_size else 0
            )
            results_text.insert(
                "end",
                (
                    f"- {category.name}: {category.file_count} files, "
                    f"{self.format_file_size(category.total_size)} "
                    f"({percentage:.1f}%)\n"
                )
            )

        self.insert_storage_items(results_text, "Largest Files", result.largest_files, "No files found.")
        self.insert_storage_items(
            results_text, "Largest Folders", result.largest_folders, "No subfolders found."
        )
        results_text.configure(state="disabled")
        results_window.focus()

    def create_results_window(self, title):
        results_window = ctk.CTkToplevel(self.app)
        results_window.title(title)
        results_window.geometry(RESULTS_WINDOW_SIZE)
        results_window.grid_columnconfigure(0, weight=1)
        results_window.grid_rowconfigure(0, weight=1)
        results_text = ctk.CTkTextbox(results_window)
        results_text.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=CONTENT_PADDING,
            pady=CONTENT_PADDING
        )
        return results_window, results_text

    def insert_storage_items(self, results_text, heading, items, empty_message):
        results_text.insert("end", f"\n{heading}\n")
        if not items:
            results_text.insert("end", f"{empty_message}\n")
            return
        for index, item in enumerate(items, start=1):
            results_text.insert(
                "end", f"{index}. {self.format_file_size(item.size)} - {item.path}\n"
            )

    @staticmethod
    def format_file_size(file_size):
        units = ("B", "KB", "MB", "GB", "TB")
        size = float(file_size)
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.1f} {unit}"
            size /= 1024

    # ---------------------------------
    # Action entry points
    # ---------------------------------

    def start_background_operation(self, target, args=()):
        self.is_processing = True
        self.sync_action_states()
        self.worker_thread = threading.Thread(target=target, args=args)
        self.worker_thread.start()
        self.app.after(100, self.process_queue)

    def selected_folder_or_warn(self):
        folder = self.folder_entry.get().strip()
        if validate_folder(folder):
            return folder
        messagebox.showwarning("Warning", "Please select a folder first.")
        return ""

    def run_organizer(self):
        if self.is_processing:
            return
        folder = self.selected_folder_or_warn()
        if not folder:
            return
        self.progress_bar.set(PROGRESS_START)
        self.set_status(STATUS_WORKING, "processing")
        self.counter_label.configure(text="Files Organized : 0")
        self.app.update_idletasks()
        self.start_background_operation(self.organize_in_background, (folder,))

    def run_undo(self):
        if self.is_processing or not self.undo_manager.can_undo():
            return
        self.progress_bar.set(PROGRESS_START)
        self.set_status(STATUS_UNDO_WORKING, "processing")
        self.counter_label.configure(text="Files Restored : 0 | Skipped : 0")
        self.app.update_idletasks()
        self.start_background_operation(self.undo_in_background)

    def run_duplicate_finder(self):
        if self.is_processing:
            return
        folder = self.selected_folder_or_warn()
        if not folder:
            return
        self.progress_bar.set(PROGRESS_START)
        self.set_status(STATUS_DUPLICATE_WORKING, "processing")
        self.counter_label.configure(text="Preparing duplicate scan...")
        self.app.update_idletasks()
        self.start_background_operation(self.find_duplicates_in_background, (folder,))

    def run_storage_analyzer(self):
        if self.is_processing:
            return
        folder = self.selected_folder_or_warn()
        if not folder:
            return
        self.progress_bar.set(PROGRESS_START)
        self.set_status(STATUS_STORAGE_WORKING, "processing")
        self.counter_label.configure(text="Preparing storage analysis...")
        self.app.update_idletasks()
        self.start_background_operation(self.analyze_storage_in_background, (folder,))

    def run(self):
        self.app.mainloop()


def start_app():
    app = SmartFileOrganizerApp()
    app.run()
