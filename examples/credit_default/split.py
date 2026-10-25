from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ID_COLUMN = "id"
TARGET_COLUMN = "default_payment_next_month"
DEFAULT_SEED = 42
PROCESSED_DATA_PATH = Path("data/processed/credit-default/v1/data.parquet")
SPLIT_ASSIGNMENTS_PATH = Path(
    "data/processed/credit-default/v1/split_assignments.parquet"
)


def create_split_assignments(
    frame: pd.DataFrame,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    required_columns = {ID_COLUMN, TARGET_COLUMN}
    missing_columns = required_columns - set(frame.columns)
    if missing_columns:
        raise ValueError(f"Required columns are missing: {sorted(missing_columns)}")

    if frame[ID_COLUMN].duplicated().any():
        raise ValueError("Record IDs must be unique")

    ordered_frame = (
        frame[[ID_COLUMN, TARGET_COLUMN]].sort_values(ID_COLUMN).reset_index(drop=True)
    )

    train_rows, remainder_rows = train_test_split(
        ordered_frame,
        test_size=0.30,
        random_state=seed,
        stratify=ordered_frame[TARGET_COLUMN],
    )

    validation_rows, test_rows = train_test_split(
        remainder_rows,
        test_size=0.50,
        random_state=seed,
        stratify=remainder_rows[TARGET_COLUMN],
    )

    assignments = pd.concat(
        [
            train_rows[[ID_COLUMN]].assign(split="train"),
            validation_rows[[ID_COLUMN]].assign(split="validation"),
            test_rows[[ID_COLUMN]].assign(split="test"),
        ],
        ignore_index=True,
    )

    return assignments.sort_values(ID_COLUMN).reset_index(drop=True)


def save_split_assignments(
    frame: pd.DataFrame,
    destination: Path,
    seed: int = DEFAULT_SEED,
) -> pd.DataFrame:
    assignments = create_split_assignments(frame, seed=seed)

    destination.parent.mkdir(parents=True, exist_ok=True)

    assignments.to_parquet(destination, index=False)

    return assignments


def main() -> None:
    frame = pd.read_parquet(PROCESSED_DATA_PATH)

    assignments = save_split_assignments(
        frame,
        SPLIT_ASSIGNMENTS_PATH,
        seed=DEFAULT_SEED,
    )

    assigned_frame = assignments.merge(
        frame[[ID_COLUMN, TARGET_COLUMN]], on=ID_COLUMN, validate="one_to_one"
    )

    print(f"dataset_path={PROCESSED_DATA_PATH}")
    print(f"assignments_path={SPLIT_ASSIGNMENTS_PATH}")
    print(f"seed={DEFAULT_SEED}")
    print(f"rows={len(assignments)}")

    for split_name in ("train", "validation", "test"):
        split_rows = assigned_frame[assigned_frame["split"] == split_name]

        prevalence = split_rows[TARGET_COLUMN].mean()

        print(
            f"{split_name}: rows={len(split_rows)}, target_prevalence={prevalence:.6f}"
        )


if __name__ == "__main__":
    main()
