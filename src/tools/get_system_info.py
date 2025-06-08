import subprocess
import shutil
from smolagents import tool

# Optional: Use psutil if available for better process info
try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


@tool
def get_system_info() -> str:
    """
    Get comprehensive system information including storage, memory, GPU, and top processes.

    Returns complete system status in one call - no parameters needed.

    Returns:
        str: Formatted system information including:
             - Disk storage usage (df)
             - RAM usage
             - GPU memory (if available)
             - Top 5 processes by resource usage
    """
    print("Gathering system information...")

    info_sections = []

    # Get storage info
    print("Checking disk storage...")
    storage_info = _get_storage_info()
    info_sections.append(f"💾 DISK STORAGE:\n{storage_info}")

    # Get RAM info
    print("Checking RAM usage...")
    ram_info = _get_ram_info()
    info_sections.append(f"🧠 RAM USAGE:\n{ram_info}")

    # Get GPU info
    print("Checking GPU memory...")
    gpu_info = _get_gpu_info()
    if gpu_info:
        info_sections.append(f"🎮 GPU MEMORY:\n{gpu_info}")

    # Get top processes
    print("Getting top processes...")
    process_info = _get_top_processes()
    info_sections.append(f"⚡ TOP 5 PROCESSES:\n{process_info}")

    result = "\n\n".join(info_sections)
    print("System information gathered successfully")
    return result


def _get_storage_info() -> str:
    """Get disk storage using df command."""
    try:
        # Use df -h for human readable format
        result = subprocess.run(['df', '-h', '--exclude-type=tmpfs', '--exclude-type=devtmpfs'],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                # Format the output nicely
                header = lines[0]
                data_lines = lines[1:]

                formatted = f"{header}\n"
                for line in data_lines:
                    formatted += f"{line}\n"

                print(f"Found {len(data_lines)} storage devices")
                return formatted.strip()
            else:
                print("No storage info in df output")
                return "No storage information available"
        else:
            print(f"df command failed: {result.stderr}")
            return f"Storage check failed: {result.stderr}"

    except Exception as e:
        error_msg = f"Failed to get storage info: {e}"
        print(error_msg)
        return error_msg


def _get_ram_info() -> str:
    """Get RAM usage from /proc/meminfo."""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()

        # Extract key memory values
        mem_total = None
        mem_available = None
        mem_free = None

        for line in meminfo.split('\n'):
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1]) * 1024  # Convert KB to bytes
            elif line.startswith('MemAvailable:'):
                mem_available = int(line.split()[1]) * 1024
            elif line.startswith('MemFree:'):
                mem_free = int(line.split()[1]) * 1024

        if mem_total and mem_available:
            mem_used = mem_total - mem_available
            usage_percent = (mem_used / mem_total) * 100

            # Convert to human readable
            total_gb = mem_total / (1024 ** 3)
            used_gb = mem_used / (1024 ** 3)
            available_gb = mem_available / (1024 ** 3)

            print(f"RAM usage: {usage_percent:.1f}%")
            return (f"Total: {total_gb:.1f}GB\n"
                    f"Used: {used_gb:.1f}GB ({usage_percent:.1f}%)\n"
                    f"Available: {available_gb:.1f}GB")
        else:
            print("Could not parse memory information")
            return "Unable to parse memory information"

    except Exception as e:
        error_msg = f"Failed to get RAM info: {e}"
        print(error_msg)
        return error_msg


def _get_gpu_info() -> str:
    """Get GPU memory info using nvidia-smi if available."""
    # Check for NVIDIA GPU
    if shutil.which('nvidia-smi'):
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free',
                                     '--format=csv,noheader,nounits'],
                                    capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpu_info = []

                for i, line in enumerate(lines):
                    if line.strip():
                        parts = line.split(', ')
                        if len(parts) == 3:
                            total, used, free = parts
                            usage_percent = (int(used) / int(total)) * 100
                            gpu_info.append(f"GPU {i}: {used}MB/{total}MB used ({usage_percent:.1f}%)")

                if gpu_info:
                    print(f"Found {len(gpu_info)} NVIDIA GPU(s)")
                    return '\n'.join(gpu_info)

        except Exception as e:
            print(f"nvidia-smi failed: {e}")

    # Check for AMD GPU (basic)
    if shutil.which('radeontop'):
        print("AMD GPU detected but detailed memory info not available via radeontop")
        return "AMD GPU detected (use radeontop for monitoring)"

    print("No GPU detected or no monitoring tools available")
    return None


def _get_top_processes() -> str:
    """Get top 5 processes by resource usage."""
    if HAS_PSUTIL:
        return _get_processes_psutil()
    else:
        return _get_processes_ps()


def _get_processes_psutil() -> str:
    """Get processes using psutil (preferred)."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 0:
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu': proc_info['cpu_percent'],
                        'memory': proc_info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage, then memory
        processes.sort(key=lambda x: (x['cpu'] + x['memory']), reverse=True)

        result = "PID     NAME                CPU%    MEM%\n"
        for proc in processes[:5]:
            result += f"{proc['pid']:<8} {proc['name'][:15]:<15} {proc['cpu']:<7.1f} {proc['memory']:<7.1f}\n"

        print(f"Found {len(processes)} active processes")
        return result.strip()

    except Exception as e:
        print(f"psutil process check failed: {e}")
        return _get_processes_ps()


def _get_processes_ps() -> str:
    """Get processes using ps command (fallback)."""
    try:
        # Get processes sorted by CPU usage
        result = subprocess.run(['ps', 'aux', '--sort=-pcpu'],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                header = "PID     NAME                CPU%    MEM%"
                process_lines = []

                for line in lines[1:6]:  # Skip header, get top 5
                    parts = line.split()
                    if len(parts) >= 11:
                        pid = parts[1]
                        cpu = parts[2]
                        mem = parts[3]
                        name = parts[10]
                        process_lines.append(f"{pid:<8} {name[:15]:<15} {cpu:<7} {mem:<7}")

                print(f"Got top 5 processes via ps command")
                return header + "\n" + "\n".join(process_lines)
            else:
                print("No process data from ps")
                return "No process information available"
        else:
            print(f"ps command failed: {result.stderr}")
            return f"Process check failed: {result.stderr}"

    except Exception as e:
        error_msg = f"Failed to get process info: {e}"
        print(error_msg)
        return error_msg