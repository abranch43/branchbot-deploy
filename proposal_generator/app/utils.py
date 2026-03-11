"""Utility helpers for the proposal generator."""

import json
import re
from pathlib import Path

from app.models import ProposalData


def load_json_file(file_path: Path) -> dict:
    """Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Parsed JSON contents as a :class:`dict`.

    Raises:
        FileNotFoundError: If *file_path* does not exist.
        ValueError: If *file_path* has the wrong extension or contains invalid JSON.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    if file_path.suffix.lower() != ".json":
        raise ValueError(
            f"Expected a .json file, got: '{file_path.suffix}' ({file_path})"
        )
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON from '{file_path}': {exc}") from exc


def sanitize_filename_component(value: str) -> str:
    """Return *value* with only alphanumeric, underscore, and hyphen characters.

    Any other character is replaced with an underscore.
    """
    return re.sub(r"[^\w\-]", "_", value)


def create_output_filename(data: ProposalData) -> str:
    """Build a deterministic output filename from *data*.

    Returns:
        A string like ``<client>_<project>_proposal.pdf``.
    """
    client = sanitize_filename_component(data.client_name)
    project = sanitize_filename_component(data.project_name)
    return f"{client}_{project}_proposal.pdf"
