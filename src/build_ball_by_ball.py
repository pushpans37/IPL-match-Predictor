import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/ball_by_ball.csv")


def get_delivery_runs(delivery):
    """Return total runs scored from a delivery."""
    return delivery.get("runs", {}).get("total", 0)


def get_batter_runs(delivery):
    """Return runs credited to the batter."""
    return delivery.get("runs", {}).get("batter", 0)


def get_wickets(delivery):
    """Return wickets recorded on a delivery."""
    return len(delivery.get("wickets", []))


def main():
    rows = []
    files = list(RAW_DIR.glob("*.json"))

    print(f"Found {len(files)} JSON files.")

    for file_path in files:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                match = json.load(file)

            info = match.get("info", {})
            innings_list = match.get("innings", [])
            teams = info.get("teams", [])
            winner = info.get("outcome", {}).get("winner")

            # We need a known winner and at least two innings
            if not winner or len(innings_list) < 2:
                continue

            # First two innings represent the regular match innings
            first_innings = innings_list[0]
            second_innings = innings_list[1]

            target = 1
            for over in first_innings.get("overs", []):
                for delivery in over.get("deliveries", []):
                    target += get_delivery_runs(delivery)

            chasing_team = second_innings.get("team")

            # Skip unusual records where the chase target cannot be established
            if not chasing_team or target <= 1:
                continue

            runs_scored = 0
            wickets_lost = 0
            legal_balls = 0

            for over in second_innings.get("overs", []):
                for ball_number, delivery in enumerate(
                    over.get("deliveries", []), start=1
                ):
                    extras = delivery.get("extras", {})
                    total_runs = get_delivery_runs(delivery)
                    batter_runs = get_batter_runs(delivery)
                    wickets = get_wickets(delivery)

                    # Illegal deliveries don't count toward the six-ball over
                    is_wide = "wides" in extras
                    is_no_ball = "noballs" in extras

                    runs_scored += total_runs
                    wickets_lost += wickets

                    if not is_wide and not is_no_ball:
                        legal_balls += 1

                    balls_remaining = max(120 - legal_balls, 0)
                    runs_remaining = max(target - runs_scored, 0)

                    # Label: did the chasing team eventually win?
                    won = int(chasing_team == winner)

                    # Exclude the final delivery so the features represent
                    # a state before the next delivery is bowled.
                    if balls_remaining > 0 and runs_remaining > 0:
                        rows.append({
                            "match_id": file_path.stem,
                            "chasing_team": chasing_team,
                            "target": target,
                            "runs_scored": runs_scored,
                            "wickets_lost": wickets_lost,
                            "legal_balls_bowled": legal_balls,
                            "balls_remaining": balls_remaining,
                            "runs_remaining": runs_remaining,
                            "current_run_rate": (
                                runs_scored * 6 / legal_balls
                                if legal_balls else 0
                            ),
                            "required_run_rate": (
                                runs_remaining * 6 / balls_remaining
                                if balls_remaining else 0
                            ),
                            "won": won,
                        })

        except (json.JSONDecodeError, OSError, TypeError, KeyError) as error:
            print(f"Could not process {file_path.name}: {error}")

    df = pd.DataFrame(rows)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved {len(df)} delivery-state rows to {OUTPUT_FILE}")
    if not df.empty:
        print("\nClass distribution:")
        print(df["won"].value_counts())
        print("\nPreview:")
        print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()