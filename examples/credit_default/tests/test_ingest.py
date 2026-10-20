from pathlib import Path

import pandas as pd
import pytest

from examples.credit_default.ingest import (
    normalize_columns,
    sha256_file,
    verify_sha256,
)


def test_sha256_file_returns_expected_digest(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.bin"
    source_file.write_bytes(b"abc")

    result = sha256_file(source_file)

    assert result == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_sha256_file_changes_when_content_changes(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.bin"
    source_file.write_bytes(b"abc")

    original_digest = sha256_file(source_file)

    source_file.write_bytes(b"abd")

    modified_digest = sha256_file(source_file)
    assert original_digest != modified_digest


def test_verify_sha256_rejects_changed_file(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "sample.bin"
    source_file.write_bytes(b"original")

    expected_sha256 = sha256_file(source_file)

    source_file.write_bytes(b"changed")

    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        verify_sha256(source_file, expected_sha256)


def test_normalize_columns_creates_expected_names() -> None:
    raw_frame = pd.DataFrame(
        {
            "ID": [1],
            "LIMIT_BAL": [20000],
            "default payment next month": [1],
        }
    )

    processed_frame = normalize_columns(raw_frame)

    assert processed_frame.columns.tolist() == [
        "id",
        "limit_bal",
        "default_payment_next_month",
    ]

    assert raw_frame.columns.tolist() == [
        "ID",
        "LIMIT_BAL",
        "default payment next month",
    ]
