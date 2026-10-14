
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path("models/ipl_chase_model.joblib")

def main():
    if not MODEL_PATH.exists():
        print("Model not found. Run: python src/train_model.py")
        return

    model = joblib.load(MODEL_PATH)

    print("\n=== IPL CHASE WIN PROBABILITY ===")
    team = input("Chasing team: ").strip()
    target = int(input("Target runs: "))
    runs_scored = int(input("Runs scored so far: "))
    wickets_lost = int(input("Wickets lost (0-10): "))
    legal_balls_bowled = int(input("Legal balls bowled (0-120): "))

    if not team:
        print("Team name cannot be empty.")
        return

    if target <= 0 or runs_scored < 0:
        print("Target must be positive and runs scored cannot be negative.")
        return

    if not 0 <= wickets_lost <= 10:
        print("Wickets lost must be between 0 and 10.")
        return

    if not 0 <= legal_balls_bowled <= 120:
        print("Legal balls bowled must be between 0 and 120.")
        return

    balls_remaining = 120 - legal_balls_bowled
    runs_remaining = max(target - runs_scored, 0)

    current_run_rate = (
        runs_scored * 6 / legal_balls_bowled
        if legal_balls_bowled > 0 else 0
    )

    required_run_rate = (
        runs_remaining * 6 / balls_remaining
        if balls_remaining > 0 else 0
    )

    match_state = pd.DataFrame([{
        "chasing_team": team,
        "target": target,
        "runs_scored": runs_scored,
        "wickets_lost": wickets_lost,
        "legal_balls_bowled": legal_balls_bowled,
        "balls_remaining": balls_remaining,
        "runs_remaining": runs_remaining,
        "current_run_rate": current_run_rate,
        "required_run_rate": required_run_rate,
    }])

    win_probability = model.predict_proba(match_state)[0][1]

    print("\n--- MATCH SITUATION ---")
    print(f"{team}: {runs_scored}/{wickets_lost}")
    print(f"Target: {target}")
    print(f"Runs remaining: {runs_remaining}")
    print(f"Balls remaining: {balls_remaining}")
    print(f"Current run rate: {current_run_rate:.2f}")
    print(f"Required run rate: {required_run_rate:.2f}")
    print(f"\nEstimated chase-win probability: {win_probability:.1%}")

if __name__ == "__main__":
    main()
