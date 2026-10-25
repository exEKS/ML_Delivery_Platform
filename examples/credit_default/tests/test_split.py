from pathlib import Path

import pandas as pd

from examples.credit_default.split import (
    create_split_assignments,
    save_split_assignments,
)


def make_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": range(1, 101),
            "default_payment_next_month": [0] * 80 + [1] * 20,
        }
    )


def test_same_seed_produces_same_assignments() -> None:
    frame = make_dataset()

    first_assignments = create_split_assignments(frame, seed=42)
    second_assignments = create_split_assignments(frame, seed=42)

    pd.testing.assert_frame_equal(first_assignments, second_assignments)


def test_split_has_expected_sizes() -> None:
    frame = make_dataset()
    assignments = create_split_assignments(frame, seed=42)

    assert len(assignments) == 100
    assert assignments["id"].is_unique
    assert assignments["split"].value_counts().to_dict() == {
        "train": 70,
        "validation": 15,
        "test": 15,
    }


def test_input_order_does_not_change_assignments() -> None:
    frame = make_dataset()
    shuffled_frame = frame.sample(frac=1.0, random_state=999).reset_index(drop=True)
    original_assignments = create_split_assignments(frame)
    shuffled_assignments = create_split_assignments(shuffled_frame)
    pd.testing.assert_frame_equal(
        original_assignments,
        shuffled_assignments,
    )


def test_target_prevalence_is_preserved_in_each_split() -> None:
    frame = make_dataset()
    assignments = create_split_assignments(frame)

    assigned_frame = assignments.merge(
        frame,
        on="id",
        validate="one_to_one",
    )

    prevalence_by_split = assigned_frame.groupby("split")[
        "default_payment_next_month"
    ].mean()

    assert (abs(prevalence_by_split - 0.20) < 0.01).all()


def test_save_split_assignments_writes_parquet(tmp_path: Path) -> None:
    frame = make_dataset()
    destination = tmp_path / "split_assignments.parquet"

    saved_assignments = save_split_assignments(frame, destination, seed=42)

    loaded_assignments = pd.read_parquet(destination)

    assert destination.is_file()
    pd.testing.assert_frame_equal(
        saved_assignments,
        loaded_assignments,
    )
