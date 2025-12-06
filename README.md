# Suraido (スライド)

[![CI](https://github.com/YOUR_USERNAME/suraido/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/suraido/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> *"The presentation treasure that awaits at the end of the Grand Line!"* 🏴‍☠️

A CLI tool to convert Beamer PDF presentations (or any PDF/PNG files) into PowerPoint (PPTX) format.

I used this tool to convert my Beamer PDF presentations to PowerPoint for my thesis defense so I could put them in Google Slides and add notes.

## Features

- **Single file or folder support** — Process individual files or entire folders
- **PDF mode** — Each PDF page becomes a slide (auto-converts at configurable DPI)
- **PNG mode** — One PNG file per slide
- **Natural sort order** — Files ordered correctly (e.g., slide1, slide2, slide10)
- **16:9 aspect ratio** — Modern widescreen slides
- **Configurable quality** — Adjust DPI for PDF conversion (default: 400)

## Installation

### Prerequisites

**For PDF support**, install `poppler`:

```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# Windows
# Download from https://github.com/oschwartz10612/poppler-windows/releases/
```

### Install with uv (recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/suraido.git
cd suraido

# Create virtual environment and install
uv venv
source .venv/bin/activate
uv sync
```

### Install with pip

```bash
pip install -e .
```

## Usage

```bash
suraido <input_path> <output_file> [--dpi DPI]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input_path` | Path to a PNG/PDF file or folder containing PNG/PDF files |
| `output_file` | Output PowerPoint file path (must end with `.pptx`) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--dpi` | 400 | DPI for PDF to PNG conversion (50-4000) |

### Examples

```bash
# Convert a Beamer PDF presentation to PowerPoint
suraido presentation.pdf slides.pptx

# Convert with higher quality
suraido presentation.pdf slides.pptx --dpi 600

# Convert a folder of PDFs
suraido ./lectures/ all_lectures.pptx

# Convert PNG screenshots to PowerPoint
suraido ./screenshots/ demo.pptx
```

## Development

### Setup

```bash
# Clone and enter the project
git clone https://github.com/YOUR_USERNAME/suraido.git
cd suraido

# Create venv and install with dev dependencies
uv venv
source .venv/bin/activate
uv sync --all-extras

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
pytest tests/ -v
```

### Linting & Formatting

```bash
# Check linting
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .

# Type checking
mypy .
```

### Pre-commit Hooks

This project uses pre-commit hooks for:
- **ruff** — Linting and formatting
- **mypy** — Static type checking
- **check-yaml** — YAML syntax validation
- **trailing-whitespace** — Remove trailing whitespace
- **end-of-file-fixer** — Ensure files end with newline

Run manually:

```bash
pre-commit run --all-files
```

## Requirements

### Python Dependencies

- Python >= 3.13
- python-pptx >= 0.6.21
- natsort >= 8.4.0
- typer >= 0.9.0
- pdf2image >= 1.16.0
- tqdm >= 4.66.0

### System Dependencies

- **poppler** — Required for PDF support (see installation above)

## License

MIT
