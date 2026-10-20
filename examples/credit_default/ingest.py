import hashlib
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd

from examples.credit_default.schema import CreditDefaultFrame

CHUNK_SIZE_BYTES = 1024 * 1024

DATASET_NAME = "credit-default"
SNAPSHOT_VERSION = "v1"
TRANSFORM_VERSION = "ingest-v1"
ID_COLUMN = "id"
TARGET_COLUMN = "default_payment_next_month"

UCI_DATASET_URL = (
    "https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients"
)
UCI_ARCHIVE_URL = (
    "https://archive.ics.uci.edu/static/public/350/"
    "default%2Bof%2Bcredit%2Bcard%2Bclients.zip"
)
UCI_XLS_ARCHIVE_MEMBER = "default of credit card clients.xls"

EXPECTED_ARCHIVE_SHA256 = (
    "56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602"
)
EXPECTED_RAW_XLS_SHA256 = (
    "30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933"
)

RAW_DATA_DIRECTORY = Path("data/raw/credit-default/v1")
RAW_ARCHIVE_PATH = RAW_DATA_DIRECTORY / "default_of_credit_card_clients.zip"
RAW_XLS_PATH = RAW_DATA_DIRECTORY / "default_of_credit_card_clients.xls"

PROCESSED_DATA_DIRECTORY = Path("data/processed/credit-default/v1")
PROCESSED_PARQUET_PATH = PROCESSED_DATA_DIRECTORY / "data.parquet"
MANIFEST_PATH = PROCESSED_DATA_DIRECTORY / "manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as source_file:
        while True:
            chunk = source_file.read(CHUNK_SIZE_BYTES)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def verify_sha256(path: Path, expected_sha256: str) -> str:
    actual_sha256 = sha256_file(path)

    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: "
            f"expected {expected_sha256}, got {actual_sha256}"
        )

    return actual_sha256


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    request = Request(
        url,
        headers={"User-Agent": "ml-delivery-platform/0.1"},
    )

    with (
        urlopen(request, timeout=60) as response,
        destination.open("wb") as destination_file,
    ):
        shutil.copyfileobj(response, destination_file)


def extract_uci_xls(archive_path: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    with (
        ZipFile(archive_path) as archive,
        archive.open(UCI_XLS_ARCHIVE_MEMBER) as archived_file,
        destination.open("wb") as destination_file,
    ):
        shutil.copyfileobj(archived_file, destination_file)


def ensure_raw_dataset() -> tuple[str, str]:
    if not RAW_ARCHIVE_PATH.exists():
        download_file(UCI_ARCHIVE_URL, RAW_ARCHIVE_PATH)

    archive_sha256 = verify_sha256(
        RAW_ARCHIVE_PATH,
        EXPECTED_ARCHIVE_SHA256,
    )

    if not RAW_XLS_PATH.exists():
        extract_uci_xls(RAW_ARCHIVE_PATH, RAW_XLS_PATH)

    raw_xls_sha256 = verify_sha256(
        RAW_XLS_PATH,
        EXPECTED_RAW_XLS_SHA256,
    )

    return archive_sha256, raw_xls_sha256


def read_raw_dataset(path: Path) -> pd.DataFrame:
    return pd.read_excel(
        path,
        sheet_name=0,
        header=1,
        engine="xlrd",
    )


def normalize_column_name(column_name: str) -> str:
    normalized = column_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)

    return normalized.strip("_")


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized_columns = [
        normalize_column_name(str(column)) for column in frame.columns
    ]

    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError("Column normalization produced duplicate column names")

    normalized_frame = frame.copy()
    normalized_frame.columns = normalized_columns

    required_columns = {ID_COLUMN, TARGET_COLUMN}
    missing_columns = required_columns - set(normalized_frame.columns)

    if missing_columns:
        raise ValueError(f"Required columns are missing: {sorted(missing_columns)}")

    return normalized_frame


def write_processed_dataset(
    frame: pd.DataFrame,
    destination: Path,
) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)

    frame.to_parquet(
        destination,
        index=False,
        engine="pyarrow",
    )

    return sha256_file(destination)


def create_manifest(
    frame: pd.DataFrame,
    raw_sha256: str,
    processed_sha256: str,
) -> dict[str, object]:
    return {
        "dataset_name": DATASET_NAME,
        "snapshot_version": SNAPSHOT_VERSION,
        "source_url": UCI_DATASET_URL,
        "source_archive_url": UCI_ARCHIVE_URL,
        "license": "CC BY 4.0",
        "created_at": datetime.now(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "raw_sha256": raw_sha256,
        "processed_sha256": processed_sha256,
        "rows": len(frame),
        "feature_count": len(
            [
                column
                for column in frame.columns
                if column not in {ID_COLUMN, TARGET_COLUMN}
            ]
        ),
        "target": TARGET_COLUMN,
        "transform_version": TRANSFORM_VERSION,
    }


def write_manifest(
    manifest: dict[str, object],
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    archive_sha256, raw_xls_sha256 = ensure_raw_dataset()

    raw_frame = read_raw_dataset(RAW_XLS_PATH)
    processed_frame = normalize_columns(raw_frame)

    processed_frame = CreditDefaultFrame.validate(
        processed_frame,
        lazy=True,
    )

    processed_sha256 = write_processed_dataset(
        processed_frame,
        PROCESSED_PARQUET_PATH,
    )

    manifest = create_manifest(
        processed_frame,
        raw_xls_sha256,
        processed_sha256,
    )
    write_manifest(manifest, MANIFEST_PATH)

    print(f"archive_path={RAW_ARCHIVE_PATH}")
    print(f"archive_sha256={archive_sha256}")
    print(f"raw_xls_path={RAW_XLS_PATH}")
    print(f"raw_xls_sha256={raw_xls_sha256}")
    print(f"processed_path={PROCESSED_PARQUET_PATH}")
    print(f"processed_sha256={processed_sha256}")
    print(f"manifest_path={MANIFEST_PATH}")
    print(f"rows={len(processed_frame)}")
    print(f"columns={len(processed_frame.columns)}")


if __name__ == "__main__":
    main()
