
from pathlib import Path
from collections import Counter
from datetime import datetime
import json
import csv

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "match_summary.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

json_files = sorted(RAW_DIR.glob("*.json"))
rows = []
errors = []

def get_innings_stats(innings):
    """Calculate total runs, wickets and deliveries for an innings."""
    total_runs = 0
    wickets = 0
    legal_balls = 0
    deliveries_count = 0

    for over in innings.get("overs", []):
        for delivery in over.get("deliveries", []):
            deliveries_count += 1
            runs = delivery.get("runs", {})
            total_runs += runs.get("total", 0)

            extras = delivery.get("extras", {})
            if "wides" not in extras and "noballs" not in extras:
                legal_balls += 1

            wickets += len(delivery.get("wickets", []))

    return total_runs, wickets, legal_balls, deliveries_count


print("=" * 60)
print("IPL DATASET SUMMARY")
print("=" * 60)
print("JSON files found:", len(json_files))

for file_path in json_files:
    try:
        with file_path.open("r", encoding="utf-8") as file:
            match = json.load(file)

        info = match.get("info", {})
        innings_list = match.get("innings", [])
        teams = info.get("teams", [])
        outcome = info.get("outcome", {})

        row = {
            "match_id": file_path.stem,
            "season": info.get("season"),
            "date": (
                info.get("dates", [None])[0]
                if info.get("dates") else None
            ),
            "venue": info.get("venue"),
            "team1": teams[0] if len(teams) > 0 else None,
            "team2": teams[1] if len(teams) > 1 else None,
            "toss_winner": info.get("toss", {}).get("winner"),
            "toss_decision": info.get("toss", {}).get("decision"),
            "winner": outcome.get("winner"),
            "innings_count": len(innings_list),
        }

        for i in range(2):
            if i < len(innings_list):
                inning = innings_list[i]
                runs, wickets, legal_balls, deliveries = (
                    get_innings_stats(inning)
                )
                row[f"innings{i + 1}_team"] = inning.get("team")
                row[f"innings{i + 1}_runs"] = runs
                row[f"innings{i + 1}_wickets"] = wickets
                row[f"innings{i + 1}_legal_balls"] = legal_balls
                row[f"innings{i + 1}_deliveries"] = deliveries
            else:
                row[f"innings{i + 1}_team"] = None
                row[f"innings{i + 1}_runs"] = None
                row[f"innings{i + 1}_wickets"] = None
                row[f"innings{i + 1}_legal_balls"] = None
                row[f"innings{i + 1}_deliveries"] = None

        rows.append(row)

    except (json.JSONDecodeError, OSError, TypeError, ValueError) as error:
        errors.append(f"{file_path.name}: {error}")

# Save the summary
if rows:
    fieldnames = list(rows[0].keys())

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# Report dataset quality
print("Matches successfully read:", len(rows))
print("Files with errors:", len(errors))

seasons = Counter(str(row["season"]) for row in rows)
print("\nMatches by season:")
for season, count in sorted(seasons.items()):
    print(f"  {season}: {count}")

missing_winners = sum(not row["winner"] for row in rows)
missing_dates = sum(not row["date"] for row in rows)
duplicate_ids = len(rows) - len({
    row["match_id"] for row in rows
})

print("\nBasic data quality checks:")
print("Matches without a recorded winner:", missing_winners)
print("Matches without a date:", missing_dates)
print("Duplicate match IDs:", duplicate_ids)

if errors:
    print("\nFirst 10 errors:")
    for error in errors[:10]:
        print(" ", error)

print("\nSummary saved to:", OUTPUT_FILE)
print("Report generated at:", datetime.now().astimezone().isoformat())
