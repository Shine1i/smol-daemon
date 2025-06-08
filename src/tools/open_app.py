from pathlib import Path
import subprocess
import shutil
import difflib
from smolagents import tool

# Import fuzzy search package
try:
    from thefuzz import process
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False
    print("Warning: thefuzz package not installed. Fuzzy search disabled.")

# --------------------------------------------------------------------------- #
# Helpers to collect application metadata                                     #
# --------------------------------------------------------------------------- #

_DESKTOP_DIRS = [
    Path("/usr/share/applications"),
    Path("/usr/local/share/applications"),
    Path.home() / ".local/share/applications",
]

def _collect_desktop_entries() -> dict[str, str]:
    """Return {launcher: human-readable name} from .desktop files."""
    out = {}
    for folder in _DESKTOP_DIRS:
        if not folder.exists():
            continue
        for f in folder.glob("*.desktop"):
            try:
                text = f.read_text("utf-8", errors="ignore")
            except Exception:
                continue
            if any(tag in text for tag in ("NoDisplay=true", "Hidden=true")):
                continue
            for line in text.splitlines():
                if line.startswith("Name="):
                    out[f.stem] = line.partition("=")[2].strip()
                    break
    return out


def _collect_flatpak_apps() -> dict[str, str]:
    """Return {app_id: display_name} for installed Flatpaks."""
    if shutil.which("flatpak") is None:
        return {}
    try:
        res = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application,name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        apps = {}
        for line in res.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split("\t") if p.strip()]
            if len(parts) >= 2:
                apps[parts[0]] = parts[1]
        return apps
    except Exception as err:
        print(f"[warn] flatpak list failed: {err}")
        return {}


def _collect_snap_apps() -> dict[str, str]:
    """Return {snap_name: snap_name}. We use the name twice for lack of summary."""
    if shutil.which("snap") is None:
        return {}
    try:
        res = subprocess.run(
            ["snap", "list", "--color=never"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = res.stdout.strip().splitlines()[1:]  # skip header
        return {ln.split()[0]: ln.split()[0] for ln in lines if ln}
    except Exception as err:
        print(f"[warn] snap list failed: {err}")
        return {}


# --------------------------------------------------------------------------- #
# Launch strategy                                                             #
# --------------------------------------------------------------------------- #

def _try_launch(name: str) -> bool:
    """Attempt to launch *name* using several strategies."""
    # 1. direct executable or snap alias
    if shutil.which(name):
        try:
            subprocess.Popen([name],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
        except Exception as err:
            print(f"[info] direct exec failed: {err}")

    # 2. gtk-launch (desktop entry)
    if shutil.which("gtk-launch"):
        try:
            if subprocess.run(["gtk-launch", name],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,
                              timeout=5).returncode == 0:
                return True
        except Exception as err:
            print(f"[info] gtk-launch failed: {err}")

    # 3. flatpak run
    if shutil.which("flatpak"):
        try:
            if subprocess.run(["flatpak", "run", name],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,
                              timeout=5).returncode == 0:
                return True
        except Exception as err:
            print(f"[info] flatpak run failed: {err}")

    # 4. snap run
    if shutil.which("snap"):
        try:
            if subprocess.run(["snap", "run", name],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,
                              timeout=5).returncode == 0:
                return True
        except Exception as err:
            print(f"[info] snap run failed: {err}")

    # 5. xdg-open fallback
    if shutil.which("xdg-open"):
        try:
            if subprocess.run(["xdg-open", name],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,
                              timeout=5).returncode == 0:
                return True
        except Exception as err:
            print(f"[info] xdg-open failed: {err}")

    return False


def _fuzzy(name: str, choices) -> str | None:
    """Return closest match for *name* among *choices*."""
    match = difflib.get_close_matches(name, choices, n=1, cutoff=0.8)
    return match[0] if match else None


def _list_apps(search_term: str = None) -> str:
    """
    List available applications from desktop files.

    Args:
        search_term: Optional term to find similar app names using fuzzy search

    Returns:
        str: List of available applications or similar matches
    """
    apps = []
    app_dict = {}  # Dictionary to store launch_name -> display_name mapping
    desktop_dirs = [
        Path("/usr/share/applications"),
        Path.home() / ".local/share/applications"
    ]

    print("Scanning for applications...")

    for apps_dir in desktop_dirs:
        if not apps_dir.exists():
            continue

        try:
            for desktop_file in apps_dir.glob("*.desktop"):
                try:
                    with open(desktop_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Skip hidden applications
                    if 'NoDisplay=true' in content or 'Hidden=true' in content:
                        continue

                    # Extract name
                    for line in content.split('\n'):
                        if line.startswith('Name=') and '=' in line:
                            display_name = line.split('=', 1)[1].strip()
                            launch_name = desktop_file.stem
                            app_entry = f"{launch_name} ({display_name})"
                            apps.append(app_entry)
                            app_dict[launch_name] = display_name
                            break

                except Exception as e:
                    print(f"Error reading {desktop_file.name}: {e}")

        except Exception as e:
            print(f"Error scanning {apps_dir}: {e}")

    if not apps:
        return "No applications found. Try common names like 'firefox', 'code', 'nautilus'."

    # If search term is provided and fuzzy search is available, find similar apps
    if search_term and HAS_FUZZY:
        print(f"Searching for apps similar to '{search_term}'...")

        # Search in launch names
        matches = process.extract(search_term, app_dict.keys(), limit=5)

        if matches:
            result = f"Similar applications to '{search_term}':\n"
            for app_name, score in matches:
                result += f"{app_name} ({app_dict[app_name]}) - {score}% match\n"
            result += "\nUse one of these names with open_app() to launch"
            return result
        else:
            return f"No similar applications found for '{search_term}'. Try a different name."

    # Regular listing of apps (no search term)
    apps.sort()
    apps_list = apps[:15]  # Limit to avoid overwhelming output
    result = f"Available applications ({len(apps_list)} shown):\n" + "\n".join(apps_list)

    if len(apps) > 15:
        result += f"\n... and {len(apps) - 15} more"

    return result


def _find_closest_app(search_term: str):
    """
    Find the closest matching app using fuzzy search.

    Args:
        search_term: Term to find similar app names

    Returns:
        tuple: (closest_app_name, score, display_name) or (None, 0, None) if no match found
    """
    app_dict = {}  # Dictionary to store launch_name -> display_name mapping
    desktop_dirs = [
        Path("/usr/share/applications"),
        Path.home() / ".local/share/applications"
    ]

    print("Scanning for applications...")

    for apps_dir in desktop_dirs:
        if not apps_dir.exists():
            continue

        try:
            for desktop_file in apps_dir.glob("*.desktop"):
                try:
                    with open(desktop_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Skip hidden applications
                    if 'NoDisplay=true' in content or 'Hidden=true' in content:
                        continue

                    # Extract name
                    for line in content.split('\n'):
                        if line.startswith('Name=') and '=' in line:
                            display_name = line.split('=', 1)[1].strip()
                            launch_name = desktop_file.stem
                            app_dict[launch_name] = display_name
                            break

                except Exception as e:
                    print(f"Error reading {desktop_file.name}: {e}")

        except Exception as e:
            print(f"Error scanning {apps_dir}: {e}")

    if not app_dict:
        return None, 0, None

    if HAS_FUZZY:
        print(f"Searching for apps similar to '{search_term}'...")

        # Search in launch names
        matches = process.extract(search_term, app_dict.keys(), limit=5)

        if matches and len(matches) > 0:
            closest_app, score = matches[0]
            return closest_app, score, app_dict[closest_app]

    return None, 0, None


# --------------------------------------------------------------------------- #
# The single-responsibility tool                                              #
# --------------------------------------------------------------------------- #

@tool
def open_app(app_name: str | None = None) -> str:
    """
    Launch a GUI application or list available apps (desktop + Flatpak + Snap).

    Args:
        app_name: Exact or approximate launcher/ID (e.g. "firefox", "org.gimp.GIMP").
                 Pass None to receive a short catalog of available applications.

    Returns:
        Success/failure notice or a list of installed applications.
    """
    desktop = _collect_desktop_entries()
    flatpaks = _collect_flatpak_apps()
    snaps = _collect_snap_apps()
    entries = {**flatpaks, **snaps, **desktop}  # desktop wins duplicates

    # -------- catalog mode ---------------------------------------------------
    if not app_name:
        sample = sorted(f"{k} ({v})" for k, v in entries.items())[:15]
        more = f"\n... and {len(entries)-15} more" if len(entries) > 15 else ""
        return "Available applications (15 shown):\n" + "\n".join(sample) + more

    # -------- launch mode ----------------------------------------------------
    key = app_name.strip().lower()
    print(f"Processing request for app: {key}")

    # Try to launch the app directly first
    if key in entries:
        if _try_launch(key):
            print(f"Success: Launched {key} directly")
            return f"Successfully launched {key}"
        else:
            print(f"Failed: Could not launch '{key}'")
            return f"Unable to launch '{key}'. It may require reinstalling or extra permissions."

    # If app not found and fuzzy search is available, try to find and launch the closest match
    print(f"App '{key}' not found. Searching for similar names...")

    # Find the closest match
    closest_app, score, display_name = _find_closest_app(key)

    # If we found a good match (score >= 80), launch it automatically
    if closest_app and score >= 80:
        print(f"Found close match: {closest_app} ({display_name}) - {score}% match. Launching automatically...")
        if _try_launch(closest_app):
            print(f"Success: Launched {closest_app} automatically")
            return f"Successfully launched {closest_app} (matched from '{app_name}')"
        else:
            print(f"Failed: Could not launch '{closest_app}'")
            return f"Unable to launch '{closest_app}'. It may require reinstalling or extra permissions."

    # Otherwise, show the list of similar apps
    if HAS_FUZZY:
        return _list_apps(key)
    else:
        return f"Application '{app_name}' not found. Run open_app() without arguments to see available apps."
