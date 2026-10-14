
import pandas as pd

df = pd.read_csv("data/processed/ball_by_ball.csv")

print("=== DATA QUALITY REPORT ===")
print("Rows:", len(df))
print("Unique matches:", df["match_id"].nunique())
print("Missing values:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())

print("\n=== RANGE CHECKS ===")
print("Invalid targets:", (df["target"] <= 0).sum())
print("Invalid wickets:", ((df["wickets_lost"] < 0) |
                           (df["wickets_lost"] > 10)).sum())
print("Invalid balls remaining:",
      ((df["balls_remaining"] < 0) |
       (df["balls_remaining"] > 120)).sum())

print("\n=== MATCH LABEL CHECK ===")
print("Matches with inconsistent labels:",
      (df.groupby("match_id")["won"].nunique() > 1).sum())

print("\n=== MATCHES BY LABEL ===")
match_labels = df.groupby("match_id")["won"].first()
print(match_labels.value_counts())

print("\n=== CHECK COMPLETE ===")
