from smolagents import tool
from pathlib import Path
from collections import defaultdict
import shutil


@tool
def organize_folder(folder_path: str) -> str:
    """
    Organizes files in a folder by moving them into subfolders based on file extensions.

    Args:
        folder_path: Path to folder to organize. Examples:
            - "~/Downloads"
            - "/home/user/Documents"
            - "/tmp/my_folder"
            - "../my_folder" (relative path)
            Can use ~ for home directory.

    Returns:
        str: Summary of files moved per extension type.
    """
    try:
        path = Path(folder_path).expanduser().resolve()
        print(f"Organizing folder: {path}")

        if not path.exists():
            raise FileNotFoundError(f"Folder not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        summary = defaultdict(int)
        for item in path.iterdir():
            if not item.is_file():
                continue

            ext = item.suffix.lstrip(".").lower() or "no_extension"
            dest_dir = path / ext
            dest_dir.mkdir(exist_ok=True)

            target = dest_dir / item.name
            if target.exists():
                base, suffix = item.stem, item.suffix
                count = 1
                while target.exists():
                    target = dest_dir / f"{base}_{count}{suffix}"
                    count += 1

            shutil.move(str(item), str(target))
            summary[ext] += 1
            print(f"Moved {item.name} to {ext}/ folder")

        if not summary:
            return f"No files to organize in {path}"

        result = f"Organized {sum(summary.values())} files in {path}:\n"
        result += "\n".join(f"{ext}: {count} files" for ext, count in sorted(summary.items()))
        return result

    except Exception as e:
        error_msg = f"Failed to organize {folder_path}: {str(e)}"
        print(error_msg)
        raise