from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def pdf_path(filename: str) -> Path:
    return PROJECT_ROOT / "pdf" / filename
