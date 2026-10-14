import pandas as pd

# Load the processed match dataset
df = pd.read_csv("data/processed/match_summary.csv")

print("=" * 60)
print("IPL DATASET VALIDATION")
print("=" * 60)

# 1. Check duplicate match IDs
print("\n1. DUPLICATE MATCH IDs")
duplicates = df[df.duplicated(subset="match_id", keep=False)]

if duplicates.empty:
    print("No duplicate match IDs found.")
else:
    print(duplicates[["match_id", "date", "team1", "team2"]]
          .to_string(index=False))

# 2. Inspect matches without a winner
print("\n2. MATCHES WITH MISSING WINNERS")
missing_winners = df[df["winner"].isna()]

print("Count:", len(missing_winners))
print(
    missing_winners[
        ["match_id", "date", "venue", "team1", "team2", "innings_count"]
    ].to_string(index=False)
)

# 3. Inspect matches with missing second-innings data
print("\n3. MATCHES WITH MISSING SECOND-INNINGS DATA")
missing_innings2 = df[df["innings2_team"].isna()]

print("Count:", len(missing_innings2))
print(
    missing_innings2[
        ["match_id", "date", "team1", "team2", "winner", "innings_count"]
    ].to_string(index=False)
)

# 4. Check innings counts
print("\n4. INNINGS COUNT DISTRIBUTION")
print(df["innings_count"].value_counts().sort_index().to_string())

# 5. Check whether the recorded winner is one of the two teams
print("\n5. WINNER CONSISTENCY")
has_winner = df["winner"].notna()

invalid_winners = df[
    has_winner
    & ~(
        df["winner"].eq(df["team1"])
        | df["winner"].eq(df["team2"])
    )
]

print("Winners not matching team1/team2:", len(invalid_winners))

if not invalid_winners.empty:
    print(
        invalid_winners[
            ["match_id", "date", "team1", "team2", "winner"]
        ].to_string(index=False)
    )

# 6. Summary
print("\n6. OVERALL SUMMARY")
print("Total matches:", len(df))
print("Unique match IDs:", df["match_id"].nunique())
print("Missing winners:", df["winner"].isna().sum())
print("Missing second innings:", df["innings2_team"].isna().sum())

print("\nValidation completed.")