# Macroeconomic Surprises and Cross-Asset Market Reactions

This project examines how U.S. CPI surprises are associated with market reactions across equities, bonds, rates, and FX.

The main research question is:

> When CPI comes in above or below consensus expectations, which asset classes react most clearly?

## Project Summary

The analysis uses U.S. CPI releases and compares market reactions across:

- Equity ETFs: SPY, QQQ
- Treasury ETF: TLT
- FX: USDJPY
- Rates: 2Y Treasury yield, 10Y Treasury yield
- Yield curve: 10Y - 2Y Treasury spread

CPI surprises are calculated as:

```text
headline_surprise = headline_actual - headline_consensus
core_surprise = core_actual - core_consensus
```

The project measures market reactions around CPI release dates and runs simple OLS regressions with heteroskedasticity-robust standard errors.

## Repository Structure

```text
macro_surprise_market_reactions/
│
├── data/
│   └── events/
│       └── cpi_surprises.csv
│
├── scripts/
│   ├── 01_data_collection.py
│   ├── 02_cpi_event_reactions.py
│   ├── 03_cpi_surprise_analysis.py
│   ├── 04_robustness_checks.py
│   ├── run_all.py
│   ├── _paths.py
│   └── _regression.py
│
├── outputs/
│   └── tables/
│       ├── event_reaction_summary.csv
│       ├── cpi_surprise_regression_results.csv
│       ├── window_robustness_results.csv
│       └── overlapping_event_sensitivity_results.csv
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Methodology

The project follows four steps:

1. Download and clean daily market data.
2. Match CPI release dates to available market trading dates.
3. Calculate cross-asset reactions across event windows.
4. Test the relationship between CPI surprises and market reactions using OLS regressions.

The main event window is:

```text
previous close to event close
```

Additional event windows are used for robustness checks.

## Key Outputs

| File | Description |
| --- | --- |
| `event_reaction_summary.csv` | Summary statistics of market reactions around CPI releases |
| `cpi_surprise_regression_results.csv` | Main event-day regression results |
| `window_robustness_results.csv` | Regression results across alternative event windows |
| `overlapping_event_sensitivity_results.csv` | Sensitivity check excluding selected overlapping event days |

## Main Finding

The results suggest that CPI surprises are more clearly reflected in USDJPY and Treasury yields than in broad equity ETFs. This is consistent with the idea that inflation surprises are more directly linked to rates and FX markets than to equity index returns.

The results should be interpreted as a small-sample event-study analysis, not as a predictive trading model.


## Limitations

- CPI consensus data is manually prepared.
- The analysis uses daily data and does not isolate intraday announcement effects.
- CPI releases may overlap with other macroeconomic events.
- The sample size is limited to the CPI releases included in the dataset.

## How to Run

From the project root:

```bash
pip install -r requirements.txt
python scripts/run_all.py
```

## Disclaimer

This project is for educational and research purposes only. It is not investment advice and does not represent a live trading strategy.
