"""CLI entry point for the proposal generator."""

import argparse
import sys
from pathlib import Path

from app.models import ProposalData
from app.pdf_generator import generate_pdf
from app.utils import create_output_filename, load_json_file


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, generate the proposal PDF, and return an exit code."""
    parser = argparse.ArgumentParser(
        prog="python -m app.main",
        description="Generate a formatted PDF proposal from a JSON input file.",
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to the JSON file containing proposal data.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        metavar="DIR",
        help="Directory where the generated PDF will be saved (default: output).",
    )

    args = parser.parse_args(argv)

    try:
        payload = load_json_file(args.input_json)
        data = ProposalData.from_dict(payload)
        filename = create_output_filename(data)
        output_path = args.output_dir / filename
        generate_pdf(data, output_path)
        print(f"Proposal PDF generated: {output_path}")
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
