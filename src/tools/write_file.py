from pathlib import Path

from smolagents import tool


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a file at the specified path.

    Args:
        file_path: Full path where to save the file. Examples:
            - "~/Documents/report.txt"
            - "/tmp/summary.log"
            - "../data/results.json"
            - "output.txt" (current directory)
            Can use ~ for home directory.
        content: String content to write to the file.

    Returns:
        str: Confirmation message with file path and size written.
    """
    try:
        path = Path(file_path).expanduser().resolve()
        print(f"Writing to file: {path}")

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = path.stat().st_size
        print(f"Successfully wrote {file_size} bytes to {path}")

        return f"File saved: {path} ({file_size} bytes)"

    except PermissionError as e:
        error_msg = f"Permission denied writing to {file_path}: {str(e)}"
        print(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to write file {file_path}: {str(e)}"
        print(error_msg)
        raise
