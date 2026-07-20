"""Recursive, read-only duplicate-file detection."""

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import os


HASH_CHUNK_SIZE = 1024 * 1024


@dataclass
class DuplicateGroup:
    """Files with identical content, ready for future user actions."""

    file_hash: str
    file_size: int
    file_paths: list[str]

    @property
    def wasted_space(self):
        """Return the space used by copies beyond the first file."""
        return self.file_size * (len(self.file_paths) - 1)


@dataclass
class DuplicateScanResult:
    """The read-only result of one duplicate scan."""

    groups: list[DuplicateGroup]
    scanned_files: int
    hashed_files: int
    skipped_files: int


def calculate_file_hash(file_path):
    """Return a SHA-256 hash while reading a file in bounded chunks."""
    file_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(HASH_CHUNK_SIZE):
            file_hash.update(chunk)

    return file_hash.hexdigest()


def find_duplicate_files(folder_path, progress_callback=None):
    """Find duplicate files recursively without modifying any file."""
    if not os.path.isdir(folder_path):
        raise NotADirectoryError("Selected folder does not exist or is invalid.")

    size_groups = defaultdict(list)
    scanned_files = 0
    skipped_files = 0

    if progress_callback:
        progress_callback("collecting", 0, 0, 0, 0)

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            try:
                file_size = os.path.getsize(file_path)
                size_groups[file_size].append(file_path)
                scanned_files += 1
            except OSError:
                skipped_files += 1

    hash_candidates = [
        (file_size, file_path)
        for file_size, paths in size_groups.items()
        if len(paths) > 1
        for file_path in paths
    ]
    total_candidates = len(hash_candidates)
    hash_groups = defaultdict(list)

    if progress_callback:
        progress_callback("hashing", 0, total_candidates, 0, 0)

    for index, (file_size, file_path) in enumerate(hash_candidates, start=1):
        try:
            file_hash = calculate_file_hash(file_path)
            hash_groups[(file_size, file_hash)].append(file_path)
        except OSError:
            skipped_files += 1

        if progress_callback:
            progress_callback("hashing", index, total_candidates, 0, 0)

    duplicate_groups = [
        DuplicateGroup(
            file_hash=file_hash,
            file_size=file_size,
            file_paths=sorted(paths)
        )
        for (file_size, file_hash), paths in hash_groups.items()
        if len(paths) > 1
    ]
    duplicate_groups.sort(
        key=lambda group: (
            -len(group.file_paths),
            -group.wasted_space,
            group.file_hash
        )
    )

    duplicate_files = sum(len(group.file_paths) for group in duplicate_groups)
    if progress_callback:
        progress_callback(
            "complete",
            total_candidates,
            total_candidates,
            len(duplicate_groups),
            duplicate_files
        )

    return DuplicateScanResult(
        groups=duplicate_groups,
        scanned_files=scanned_files,
        hashed_files=total_candidates,
        skipped_files=skipped_files
    )
