import os
import shutil


def organize_files(folder_path):

    if not os.path.exists(folder_path):
        print("Folder not found!")
        return

    file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov"],
        "Audio": [".mp3", ".wav", ".aac"],
        "Archives": [".zip", ".rar", ".7z"]
    }

    # Create folders
    for folder_name in file_types:

        folder = os.path.join(folder_path, folder_name)

        if not os.path.exists(folder):
            os.makedirs(folder)

    # Organize files
    for file in os.listdir(folder_path):

        source_path = os.path.join(folder_path, file)

        if os.path.isdir(source_path):
            continue

        _, extension = os.path.splitext(file)
        extension = extension.lower()

        for folder_name, extensions in file_types.items():

            if extension in extensions:

                destination = os.path.join(folder_path, folder_name, file)

                if not os.path.exists(destination):
                    shutil.move(source_path, destination)

                break

    print("Organization Complete!")