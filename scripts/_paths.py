from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_DIR / "data"
EVENTS_DIR = DATA_DIR / "events"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_DIR / "outputs"
TABLES_DIR = OUTPUT_DIR / "tables"


def ensure_project_directories() -> None:
    """Create project output directories if they do not already exist."""
    for folder in [EVENTS_DIR, PROCESSED_DIR, TABLES_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
