# Proposal Generator

A lightweight Python CLI tool that reads proposal data from a JSON file and produces a formatted PDF using [ReportLab](https://www.reportlab.com/).

## Features

- JSON-driven input with strict field validation
- Clean, professional PDF layout (Letter size)
- Automatic output filename derived from client and project names
- Clear error messages for missing or malformed input

## Folder Structure

```
proposal_generator/
├── app/
│   ├── __init__.py       # Package marker
│   ├── main.py           # CLI entry point
│   ├── models.py         # ProposalData dataclass & validation
│   ├── pdf_generator.py  # ReportLab PDF rendering
│   └── utils.py          # File loading & filename helpers
├── data/
│   └── sample_input.json # Example input file
├── output/               # Generated PDFs land here (git-ignored)
│   └── .gitkeep
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Usage

Run commands from inside the `proposal_generator/` directory.

**Default output directory (`output/`):**
```bash
python -m app.main data/sample_input.json
```

**Custom output directory:**
```bash
python -m app.main data/sample_input.json --output-dir /path/to/output
```

**Help:**
```bash
python -m app.main --help
```

## Output Filename

The PDF filename is derived automatically from the input data:

```
{client_name}_{project_name}_proposal.pdf
```

Special characters in the client or project name are replaced with underscores.

**Example:** client `Acme Corporation`, project `E-Commerce Platform Redesign`
→ `Acme_Corporation_E-Commerce_Platform_Redesign_proposal.pdf`

## Input JSON Schema

| Field           | Type   | Description                              |
|-----------------|--------|------------------------------------------|
| `client_name`   | string | Name of the client                       |
| `project_name`  | string | Name of the project                      |
| `scope_of_work` | string | Detailed scope (newlines supported)      |
| `price`         | number | Proposed price (non-negative)            |
| `date`          | string | Proposal date in `YYYY-MM-DD` format     |

## Expansion Ideas

- Add a company logo to the PDF header
- Support multiple-currency formatting
- Generate a cover page with branding
- Export to DOCX in addition to PDF
- Build a web UI with FastAPI and a simple HTML form
