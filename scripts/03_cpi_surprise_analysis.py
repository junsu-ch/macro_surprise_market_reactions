import pandas as pd

from _paths import EVENTS_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_directories
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

    cpi_path = EVENTS_DIR / "cpi_surprises.csv"
    reactions_path = PROCESSED_DIR / "event_reactions.csv"

    cpi = pd.read_csv(cpi_path, parse_dates=["event_date"])
    reactions = pd.read_csv(
        reactions_path,
        parse_dates=["event_date", "market_date", "window_start", "window_end"],
    )

    cpi = cpi.sort_values("event_date").reset_index(drop=True).copy()

    cpi["headline_surprise"] = cpi["headline_actual"] - cpi["headline_consensus"]
    cpi["core_surprise"] = cpi["core_actual"] - cpi["core_consensus"]

    surprise_columns = [
        "event_date",
        "reference_period",
        "headline_actual",
        "headline_consensus",
        "headline_surprise",
        "core_actual",
        "core_consensus",
        "core_surprise",
    ]

    cpi_surprises = cpi[surprise_columns].copy()

    analysis_data = reactions.merge(
        cpi_surprises,
        on=["event_date", "reference_period"],
        how="inner",
    )

    analysis_data = analysis_data.sort_values(["event_date", "window"]).reset_index(drop=True)
    event_day_data = analysis_data[analysis_data["window"].eq(MAIN_WINDOW)].copy()

    regression_results = run_regression_table(
        event_day_data,
        DEPENDENT_VARIABLES,
        SURPRISE_VARIABLES,
    )

    analysis_data_path = PROCESSED_DIR / "cpi_surprise_analysis_data.csv"
    event_day_data_path = PROCESSED_DIR / "cpi_surprise_event_day_regression_data.csv"
    regression_results_path = TABLES_DIR / "cpi_surprise_regression_results.csv"

    analysis_data.to_csv(analysis_data_path, index=False)
    event_day_data.to_csv(event_day_data_path, index=False)
    regression_results.to_csv(regression_results_path, index=False)

    print(f"Saved analysis data to: {analysis_data_path}")
    print(f"Saved event-day regression data to: {event_day_data_path}")
    print(f"Saved regression results to: {regression_results_path}")
    print(regression_results)


if __name__ == "__main__":
    main()
