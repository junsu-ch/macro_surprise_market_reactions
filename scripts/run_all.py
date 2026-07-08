import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "01_data_collection.py",
    "02_cpi_event_reactions.py",
    "03_cpi_surprise_analysis.py",
    "04_robustness_checks.py",
]


def main() -> None:
    scripts_dir = Path(__file__).resolve().parent

    for script in SCRIPTS:
        script_path = scripts_dir / script
        print(f"\nRunning {script}...")
        subprocess.run([sys.executable, str(script_path)], check=True)

    print("\nAll scripts completed successfully.")


if __name__ == "__main__":
    main()
