
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
    brier_score_loss,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import GroupShuffleSplit

DATA_PATH = Path("data/processed/ball_by_ball.csv")
MODEL_PATH = Path("models/ipl_chase_model.joblib")

FEATURES = [
    "chasing_team",
    "target",
    "runs_scored",
    "wickets_lost",
    "legal_balls_bowled",
    "balls_remaining",
    "runs_remaining",
    "current_run_rate",
    "required_run_rate",
]

NUMERIC_FEATURES = [f for f in FEATURES if f != "chasing_team"]
CATEGORICAL_FEATURES = ["chasing_team"]


def main():
    df = pd.read_csv(DATA_PATH)

    # Split by match, so states from the same match don't appear
    # in both training and testing sets.
    splitter = GroupShuffleSplit(
        n_splits=1, test_size=0.2, random_state=42
    )
    train_idx, test_idx = next(
        splitter.split(df, df["won"], groups=df["match_id"])
    )

    train = df.iloc[train_idx]
    test = df.iloc[test_idx]

    X_train = train[FEATURES]
    y_train = train["won"]
    X_test = test[FEATURES]
    y_test = test["won"]

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessing = ColumnTransformer([
        ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
    ])

    model = Pipeline([
        ("preprocessing", preprocessing),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("=== IPL CHASE MODEL RESULTS ===")
    print(f"Training rows: {len(train):,}")
    print(f"Testing rows: {len(test):,}")
    print(f"Training matches: {train['match_id'].nunique():,}")
    print(f"Testing matches: {test['match_id'].nunique():,}")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.4f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")
    print(f"Brier score: {brier_score_loss(y_test, probabilities):.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
