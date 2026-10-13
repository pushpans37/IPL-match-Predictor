
from pathlib import Path
from datetime import datetime
import json
import csv

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
LOG_FILE = PROJECT_DIR / "inspection_log.txt"

def log(message=""):
    """Append each message to the inspection log."""
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(message + "\n")

# Append a timestamped report instead of overwriting the old report
run_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

log("\n" + "=" * 70)
log(f"IPL MATCH PREDICTOR - INSPECTION REPORT")
log(f"Inspection date and time: {run_time}")
log(f"Project folder: {PROJECT_DIR}")
log("=" * 70)

print("IPL MATCH PREDICTOR - FILE INSPECTION")
print("Inspection time:", run_time)
print("Searching:", DATA_DIR)

if not DATA_DIR.exists():
    message = f"ERROR: Data folder not found: {DATA_DIR}"
    print(message)
    log(message)
else:
    files = sorted(
        path for path in DATA_DIR.rglob("*")
        if path.is_file()
    )

    print(f"\nTotal files found: {len(files)}")
    log(f"Total files found: {len(files)}")

    if not files:
        message = "No files found inside the data folder."
        print(message)
        log(message)

    for path in files:
        modified = datetime.fromtimestamp(
            path.stat().st_mtime
        ).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

        size = path.stat().st_size
        relative_path = path.relative_to(PROJECT_DIR)

        details = (
            f"\nFile: {relative_path}\n"
            f"Last modified: {modified}\n"
            f"Size: {size:,} bytes"
        )

        print(details)
        log(details)

        try:
            if path.suffix.lower() == ".csv":
                with path.open(
                    "r", encoding="utf-8-sig", newline=""
                ) as file:
                    reader = csv.reader(file)
                    headers = next(reader, [])
                    log(f"CSV columns: {headers}")
                    print("CSV columns:", headers)

            elif path.suffix.lower() == ".json":
                with path.open(
                    "r", encoding="utf-8-sig"
                ) as file:
                    content = json.load(file)

                summary = (
                    f"JSON root type: {type(content).__name__}"
                )
                log(summary)
                print(summary)

                if isinstance(content, dict):
                    keys = list(content.keys())
                    log(f"JSON top-level keys: {keys}")
                    print("JSON top-level keys:", keys)

                elif isinstance(content, list):
                    log(f"JSON list items: {len(content)}")
                    print("JSON list items:", len(content))

            elif path.name.lower() == "readme" or (
                path.name.lower().startswith("readme.")
            ):
                with path.open(
                    "r", encoding="utf-8-sig", errors="replace"
                ) as file:
                    preview = file.read(2000)

                log("README preview (up to 2000 characters):")
                log(preview)
                print("README preview:")
                print(preview[:500])

        except Exception as error:
            error_message = (
                f"Could not inspect {relative_path}: {error}"
            )
            print(error_message)
            log(error_message)

print(f"\nReport appended to: {LOG_FILE}")
