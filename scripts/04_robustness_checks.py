import pandas as pd

from _paths import PROCESSED_DIR, TABLES_DIR, ensure_project_directories
from _regression import run_regression_table


MAIN_WINDOW = "prev_close_to_event_close"

DEPENDENT_VARIABLES = [
    "spy_pct",
    "qqq_pct",
    "tlt_pct",
    "usdjpy_pct",
    "dgs2_bp",
    "dgs10_bp",
    "yield_curve_10y2y_bp",
]

SURPRISE_VARIABLES = [
    "headline_surprise",
    "core_surprise",
]


def main() -> None:
    ensure_project_directories()

    analysis_path = PROCESSED_DIR / "cpi_surprise_analysis_data.csv"

    analysis_data = pd.read_csv(
        analysis_path,
        parse_dates=["event_date", "market_date", "window_start", "window_end"],
    )

    window_rows = []

    for window_name, window_data in analysis_data.groupby("window"):
        result = run_regression_table(
            window_data,
            DEPENDENT_VARIABLES,
            SURPRISE_VARIABLES,
        )

        result.insert(0, "window", window_name)
        window_rows.append(result)

    window_robustness = pd.concat(window_rows, ignore_index=True)

    event_day_data = analysis_data[analysis_data["window"].eq(MAIN_WINDOW)].copy()

    all_events = run_regression_table(
        event_day_data,
        DEPENDENT_VARIABLES,
        SURPRISE_VARIABLES,
    )
    all_events.insert(0, "sample", "all_events")

    clean_events = run_regression_table(
        event_day_data[~event_day_data["overlapping_event_day"]],
        DEPENDENT_VARIABLES,
        SURPRISE_VARIABLES,
    )
    clean_events.insert(0, "sample", "excluding_overlapping_event_days")

    overlapping_sensitivity = pd.concat(
        [all_events, clean_events],
        ignore_index=True,
    )

    window_robustness_path = TABLES_DIR / "window_robustness_results.csv"
    overlapping_sensitivity_path = TABLES_DIR / "overlapping_event_sensitivity_results.csv"

    window_robustness.to_csv(window_robustness_path, index=False)
    overlapping_sensitivity.to_csv(overlapping_sensitivity_path, index=False)

    print(f"Saved window robustness results to: {window_robustness_path}")
    print(f"Saved overlapping event sensitivity results to: {overlapping_sensitivity_path}")
    print(window_robustness)
    print(overlapping_sensitivity)


if __name__ == "__main__":
    main()
