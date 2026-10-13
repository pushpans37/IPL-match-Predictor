
from pathlib import Path
import json

# Locate the project and raw data folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

# Find the first JSON match file
json_files = sorted(DATA_DIR.glob("*.json"))

if not json_files:
    print("No JSON files found!")
    raise SystemExit(1)

match_file = json_files[0]

print("=" * 60)
print("IPL MATCH JSON INSPECTOR")
print("=" * 60)
print("File:", match_file.name)
print("Path:", match_file)
print()

# Read the JSON file
with match_file.open("r", encoding="utf-8") as file:
    match_data = json.load(file)

# Display the top-level structure
print("TOP-LEVEL KEYS:")
for key in match_data:
    print("-", key)

# Display match information
print("\nMATCH INFORMATION:")
info = match_data.get("info", {})

print("Teams:", info.get("teams"))
print("Dates:", info.get("dates"))
print("Venue:", info.get("venue"))
print("City:", info.get("city"))
print("Season:", info.get("season"))
print("Toss:", info.get("toss"))
print("Outcome:", info.get("outcome"))

# Display innings information
print("\nINNINGS INFORMATION:")
innings = match_data.get("innings", [])

print("Number of innings:", len(innings))

for index, inning in enumerate(innings, start=1):
    print(f"\nInnings {index}")
    print("Batting team:", inning.get("team"))

    overs = inning.get("overs", [])
    print("Number of overs recorded:", len(overs))

    if overs:
        first_over = overs[0]
        print("First over number:", first_over.get("over"))

        deliveries = first_over.get("deliveries", [])
        print("Deliveries recorded in first over:", len(deliveries))

        if deliveries:
            print("First delivery:")
            print(json.dumps(deliveries[0], indent=2))

print("\nInspection completed!")
