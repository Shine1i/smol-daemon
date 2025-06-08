import subprocess

from smolagents import tool


@tool
def clean_system(preview: bool = False) -> str:
    """
    Runs system cleanup using BleachBit CLI to free up disk space.

    Args:
        preview: If True, shows what would be cleaned without actually cleaning.
                If False, performs the actual cleanup. Default is False.

    Returns:
        str: Summary of cleanup results or preview of what would be cleaned.
    """
    action = "preview" if preview else "clean"
    print(f"Running BleachBit {action}...")

    try:
        # Check if BleachBit is available
        check_result = subprocess.run(["which", "bleachbit"], capture_output=True, text=True)
        if check_result.returncode != 0:
            raise FileNotFoundError("BleachBit not found. Install with: sudo apt install bleachbit")

        # Run preview or actual cleanup
        cmd = ["bleachbit", "--preview", "--preset"] if preview else ["bleachbit", "--clean", "--preset"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        print(f"BleachBit finished with exit code: {result.returncode}")

        output_lines = (result.stdout or result.stderr or f"BleachBit {action} completed (no detailed output)").strip().splitlines()
        output_tail = "\n".join(output_lines[-3:])  # Last 10 lines

        if result.returncode != 0:
            print(f"Warning: exit code {result.returncode}")
            return f"BleachBit {action} completed with warnings:\n{output_tail}"

        return f"BleachBit {action} successful:\n{output_tail}"

    except subprocess.TimeoutExpired:
        error_msg = f"BleachBit {action} timed out after 5 minutes"
        print(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"BleachBit {action} failed: {str(e)}"
        print(error_msg)
        raise
