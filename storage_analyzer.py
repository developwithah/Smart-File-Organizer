"""Read-only recursive storage analysis."""

from collections import defaultdict
from dataclasses import dataclass
import heapq
import os


CATEGORY_EXTENSIONS = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"},
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls",
        ".xlsx", ".csv", ".odt"
    },
    "Music": {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"}
}
CATEGORY_NAMES = (*CATEGORY_EXTENSIONS.keys(), "Others")
TOP_ITEM_LIMIT = 10


@dataclass
class StorageCategory:
    """Storage totals for one file category."""

    name: str
    file_count: int = 0
    total_size: int = 0


@dataclass
class StorageItem:
    """A file or folder and its size in bytes."""

    path: str
    size: int


@dataclass
class StorageAnalysis:
    """Complete, read-only storage analysis for a selected folder."""

    total_files: int
    total_folders: int
    total_size: int
    categories: list[StorageCategory]
    largest_files: list[StorageItem]
    largest_folders: list[StorageItem]
    skipped_files: int


def categorize_file(file_path):
    """Return the reporting category for a file extension."""
    extension = os.path.splitext(file_path)[1].lower()

    for category, extensions in CATEGORY_EXTENSIONS.items():
        if extension in extensions:
            return category

    return "Others"


def analyze_storage(folder_path, progress_callback=None):
    """Recursively calculate storage totals without changing any files."""
    if not os.path.isdir(folder_path):
        raise NotADirectoryError("Selected folder does not exist or is invalid.")

    file_paths = []
    folder_paths = {folder_path}

    if progress_callback:
        progress_callback("collecting", 0, 0, 0)

    for root, folders, files in os.walk(folder_path):
        folder_paths.add(root)
        for folder in folders:
            folder_paths.add(os.path.join(root, folder))
        for file_name in files:
            file_paths.append(os.path.join(root, file_name))

    categories = {
        name: StorageCategory(name=name)
        for name in CATEGORY_NAMES
    }
    folder_sizes = defaultdict(int)
    file_items = []
    total_size = 0
    skipped_files = 0
    total_files = len(file_paths)

    if progress_callback:
        progress_callback("analyzing", 0, total_files, 0)

    for index, file_path in enumerate(file_paths, start=1):
        try:
            file_size = os.path.getsize(file_path)
            category = categories[categorize_file(file_path)]
            category.file_count += 1
            category.total_size += file_size
            total_size += file_size
            file_items.append(StorageItem(path=file_path, size=file_size))
            folder_sizes[os.path.dirname(file_path)] += file_size

        except OSError:
            skipped_files += 1

        if progress_callback:
            progress_callback("analyzing", index, total_files, total_size)

    for folder_path_item in sorted(
        folder_paths,
        key=lambda path: len(os.path.normpath(path).split(os.sep)),
        reverse=True
    ):
        parent_folder = os.path.dirname(folder_path_item)
        if parent_folder in folder_paths:
            folder_sizes[parent_folder] += folder_sizes[folder_path_item]

    largest_files = heapq.nlargest(
        TOP_ITEM_LIMIT,
        file_items,
        key=lambda item: (item.size, item.path)
    )
    largest_folders = heapq.nlargest(
        TOP_ITEM_LIMIT,
        (
            StorageItem(path=path, size=folder_sizes[path])
            for path in folder_paths
            if path != folder_path
        ),
        key=lambda item: (item.size, item.path)
    )

    return StorageAnalysis(
        total_files=total_files - skipped_files,
        total_folders=len(folder_paths) - 1,
        total_size=total_size,
        categories=[categories[name] for name in CATEGORY_NAMES],
        largest_files=largest_files,
        largest_folders=largest_folders,
        skipped_files=skipped_files
    )
