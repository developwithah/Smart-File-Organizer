import os
import shutil


FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audio": [".mp3", ".wav", ".aac"],
    "Archives": [".zip", ".rar", ".7z"]
}


def organize_files(folder_path, progress_callback=None, move_callback=None):
    """
    Organize files into category folders.

    Parameters:
        folder_path (str)
        progress_callback (function)
        move_callback (function)

    Returns:
        int -> Number of files organized
    """

    if not os.path.exists(folder_path):
        raise FileNotFoundError("Selected folder does not exist.")

    # Create category folders
    for folder in FILE_TYPES:
        os.makedirs(
            os.path.join(folder_path, folder),
            exist_ok=True
        )

    files = []

    for item in os.listdir(folder_path):

        full_path = os.path.join(folder_path, item)

        if os.path.isfile(full_path):
            files.append(item)

    total_files = len(files)

    moved_files = 0

    if total_files == 0:

        if progress_callback:
            progress_callback(1, 0)

        return 0

    for index, file in enumerate(files, start=1):

        source = os.path.join(folder_path, file)

        _, extension = os.path.splitext(file)

        extension = extension.lower()

        for category, extensions in FILE_TYPES.items():

            if extension in extensions:

                destination = os.path.join(
                    folder_path,
                    category,
                    file
                )

                if not os.path.exists(destination):

                    shutil.move(source, destination)
                    moved_files += 1

                    if move_callback:
                        move_callback(source, destination)

                break

        if progress_callback:

            progress = index / total_files

            progress_callback(
                progress,
                moved_files
            )

    return moved_files
