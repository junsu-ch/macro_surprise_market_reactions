import numpy as np
import pandas as pd

from _paths import EVENTS_DIR, PROCESSED_DIR, TABLES_DIR, ensure_project_directories


FOMC_DATES = pd.to_datetime([
    "2024-01-31",
    "2024-03-20",
    "2024-05-01",
    "2024-06-12",
    "2024-07-31",
    "2024-09-18",
    "2024-11-07",
    "2024-12-18",
    "2025-01-29",
    "2025-03-19",
    "2025-05-07",
    "2025-06-18",
    "2025-07-30",
    "2025-09-17",
    "2025-10-29",
    "2025-12-10",
    "2026-01-28",
    "2026-03-18",
    "2026-04-29",
    "2026-06-17",
])

EVENT_WINDOWS = {
    "prev_close_to_event_close": (-1, 0),
    "event_close_to_next_close": (0, 1),
    "event_close_to_5d_after": (0, 5),
    "5d_before_to_5d_after": (-5, 5),
}

PRICE_COLUMNS = ["spy", "qqq", "tlt", "usdjpy"]
YIELD_COLUMNS = ["dgs2", "dgs10", "yield_curve_10y2y"]
REACTION_COLUMNS = [
    "spy_pct",
    "qqq_pct",
    "tlt_pct",
    "usdjpy_pct",
    "dgs2_bp",
    "dgs10_bp",
    "yield_curve_10y2y_bp",
]


def next_market_date(event_date: pd.Timestamp, available_dates: pd.DatetimeIndex) -> pd.Timestamp:
    position = available_dates.searchsorted(event_date)

    if position == len(available_dates):
        return pd.NaT

    return available_dates[position]


def get_window_dates(
    market_date: pd.Timestamp,
    start_offset: int,
    end_offset: int,
    available_dates: pd.DatetimeIndex,
) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    position = available_dates.get_loc(market_date)

    start_position = position + start_offset
    end_position = position + end_offset

    if start_position < 0 or end_position >= len(available_dates):
        return None, None

    return available_dates[start_position], available_dates[end_position]


def calculate_reaction(
    event_row: pd.Series,
    window_name: str,
    start_offset: int,
    end_offset: int,
    market_data: pd.DataFrame,
    market_dates: pd.DatetimeIndex,
) -> dict | None:
    start_date, end_date = get_window_dates(
        event_row["market_date"],
        start_offset,
        end_offset,
        market_dates,
    )

    if start_date is None or end_date is None:
        return None

    start_values = market_data.loc[start_date]
    end_values = market_data.loc[end_date]

    row = {
        "event_date": event_row["event_date"],
        "market_date": event_row["market_date"],
        "reference_period": event_row["reference_period"],
        "window": window_name,
        "window_start": start_date,
        "window_end": end_date,
        "overlapping_event_day": event_row["overlapping_event_day"],
    }

    for column in PRICE_COLUMNS:
        row[f"{column}_pct"] = np.log(end_values[column] / start_values[column]) * 100

    for column in YIELD_COLUMNS:
        row[f"{column}_bp"] = (end_values[column] - start_values[column]) * 100

    return row


def main() -> None:
    ensure_project_directories()

    market_path = PROCESSED_DIR / "market_data.csv"
    cpi_path = EVENTS_DIR / "cpi_surprises.csv"

    market_data = pd.read_csv(
        market_path,
        parse_dates=["date"],
        index_col="date",
    ).sort_index()

    market_columns = PRICE_COLUMNS + YIELD_COLUMNS
    market_data = market_data.dropna(subset=market_columns).copy()
    market_dates = market_data.index

    cpi_events = pd.read_csv(cpi_path, parse_dates=["event_date"])
    cpi_events = cpi_events.sort_values("event_date").reset_index(drop=True)

    cpi_events["market_date"] = cpi_events["event_date"].apply(
        lambda date: next_market_date(date, market_dates)
    )
    cpi_events["overlapping_event_day"] = cpi_events["event_date"].isin(FOMC_DATES)

    rows = []

    for _, event_row in cpi_events.dropna(subset=["market_date"]).iterrows():
        for window_name, offsets in EVENT_WINDOWS.items():
            start_offset, end_offset = offsets

            row = calculate_reaction(
                event_row,
                window_name,
                start_offset,
                end_offset,
                market_data,
                market_dates,
            )

            if row is not None:
                rows.append(row)

    event_reactions = pd.DataFrame(rows)

    summary = (
        event_reactions
        .groupby("window")
        .agg(
            event_count=("event_date", "count"),
            overlapping_event_count=("overlapping_event_day", "sum"),
            **{f"{column}_mean": (column, "mean") for column in REACTION_COLUMNS},
            **{f"{column}_median": (column, "median") for column in REACTION_COLUMNS},
        )
        .reset_index()
    )

    event_reactions_path = PROCESSED_DIR / "event_reactions.csv"
    summary_path = TABLES_DIR / "event_reaction_summary.csv"

    event_reactions.to_csv(event_reactions_path, index=False)
    summary.to_csv(summary_path, index=False)

    print(f"Saved event reactions to: {event_reactions_path}")
    print(f"Saved summary to: {summary_path}")
    print(summary)


if __name__ == "__main__":
    main()
