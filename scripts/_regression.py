import pandas as pd
import statsmodels.api as sm


def run_regression_table(
    data: pd.DataFrame,
    dependent_variables: list[str],
    surprise_variables: list[str],
) -> pd.DataFrame:
    """Run simple OLS regressions with HC1 robust standard errors."""
    rows = []

    for dependent_variable in dependent_variables:
        for surprise_variable in surprise_variables:
            regression_data = data[[dependent_variable, surprise_variable]].dropna()

            if len(regression_data) < 3:
                continue

            y = regression_data[dependent_variable]
            x = sm.add_constant(regression_data[surprise_variable])

            model = sm.OLS(y, x).fit(cov_type="HC1")

            rows.append({
                "dependent_variable": dependent_variable,
                "surprise_variable": surprise_variable,
                "nobs": int(model.nobs),
                "coefficient": model.params[surprise_variable],
                "std_error": model.bse[surprise_variable],
                "t_stat": model.tvalues[surprise_variable],
                "p_value": model.pvalues[surprise_variable],
                "r_squared": model.rsquared,
            })

    return pd.DataFrame(rows)
