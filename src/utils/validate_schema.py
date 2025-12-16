import json
import logging
from pathlib import Path
from typing import Tuple

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError


# -----------------------------------------------------------------------------
# Logging Configuration (Production Ready)
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Core Validation Function
# -----------------------------------------------------------------------------
def validate_schema(
    schema_path: str | Path,
    jsonl_path: str | Path
) -> Tuple[int, int]:
    """
    Validate a JSONL file against a JSON Schema.

    Args:
        schema_path (str | Path): Path to JSON schema file
        jsonl_path (str | Path): Path to JSONL data file

    Returns:
        Tuple[int, int]: (valid_records, invalid_records)
    """

    schema_path = Path(schema_path)
    jsonl_path = Path(jsonl_path)

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    if not jsonl_path.exists():
        raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

    # Load schema
    with schema_path.open(encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    validator = Draft7Validator(schema)

    valid_count = 0
    invalid_count = 0

    with jsonl_path.open(encoding="utf-8") as jsonl_file:
        for line_number, line in enumerate(jsonl_file, start=1):

            if not line.strip():
                continue  # Skip empty lines

            try:
                record = json.loads(line)

            except json.JSONDecodeError as exc:
                invalid_count += 1
                logger.error(
                    "JSON decode error at line %d | %s",
                    line_number,
                    exc.msg
                )
                continue

            errors = sorted(
                validator.iter_errors(record),
                key=lambda e: list(e.path)
            )

            if not errors:
                valid_count += 1
                continue

            invalid_count += 1
            for error in errors:
                error_path = " -> ".join(map(str, error.path)) or "ROOT"
                logger.error(
                    "Schema validation error at line %d | Path: %s | Reason: %s",
                    line_number,
                    error_path,
                    error.message
                )

    logger.info("========== VALIDATION SUMMARY ==========")
    logger.info("Valid records   : %d", valid_count)
    logger.info("Invalid records : %d", invalid_count)

    return valid_count, invalid_count