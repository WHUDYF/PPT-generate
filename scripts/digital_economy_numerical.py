#!/usr/bin/env python3
"""Numerical analysis for the digital economy course presentation.

The data and formulas match `digital_economy_numerical_20260519_113555.pptx`:
three-point finite differences, segmented least-squares fitting, Pearson
correlation, and short-term recovery-scenario prediction.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class DataPoint:
    year: int
    museums: float
    visitors_million: float
    tourism_spending_100m_yuan: float
    stage: str


DATA: list[DataPoint] = [
    DataPoint(2014, 3658, 3611, 30311.9, "增长期"),
    DataPoint(2015, 3852, 4000, 34195.1, "增长期"),
    DataPoint(2016, 4109, 4440, 39390.0, "增长期"),
    DataPoint(2017, 4721, 5001, 45660.9, "增长期"),
    DataPoint(2018, 4918, 5539, 51278.3, "增长期"),
    DataPoint(2019, 5132, 6006, 57251.0, "高点"),
    DataPoint(2020, 5446, 2879, 22286.3, "冲击"),
    DataPoint(2021, 5772, 3246, 29191.0, "修复"),
    DataPoint(2022, 6565, 2530, 20444.0, "波动"),
    DataPoint(2023, 6833, 4891, 49133.1, "修复"),
]


METRIC_LABELS = {
    "museums": "博物馆数量",
    "visitors_million": "国内游客",
    "tourism_spending_100m_yuan": "旅游总花费",
}


def three_point_diff(values: Sequence[float], h: float = 1.0) -> list[float]:
    """Return finite-difference estimates using a three-point center formula.

    Internal points use (f[i + 1] - f[i - 1]) / (2h). Endpoints use one-sided
    first-order differences so every year keeps a reported marginal change.
    """
    if len(values) < 2:
        raise ValueError("at least two values are required")
    if h <= 0:
        raise ValueError("h must be positive")

    diff: list[float] = []
    for i, value in enumerate(values):
        if i == 0:
            diff.append((values[1] - value) / h)
        elif i == len(values) - 1:
            diff.append((value - values[-2]) / h)
        else:
            diff.append((values[i + 1] - values[i - 1]) / (2 * h))
    return diff


def least_squares_line(x_values: Sequence[float], y_values: Sequence[float]) -> tuple[float, float]:
    """Fit y = a*x + b by ordinary least squares."""
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have the same length")
    if len(x_values) < 2:
        raise ValueError("at least two points are required")

    n = len(x_values)
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    if math.isclose(denominator, 0):
        raise ValueError("x values cannot all be equal")
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept


def least_squares_polynomial(
    x_values: Sequence[float],
    y_values: Sequence[float],
    degree: int,
) -> list[float]:
    """Fit a low-degree polynomial by ordinary least squares.

    Coefficients are returned in ascending power order:
    c[0] + c[1] * x + c[2] * x**2 ...
    """
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have the same length")
    if degree < 0:
        raise ValueError("degree must be non-negative")
    if len(x_values) <= degree:
        raise ValueError("number of points must exceed polynomial degree")

    size = degree + 1
    matrix = [
        [sum(x ** (row + col) for x in x_values) for col in range(size)]
        for row in range(size)
    ]
    vector = [sum(y * (x ** row) for x, y in zip(x_values, y_values)) for row in range(size)]

    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(augmented[row][col]))
        if math.isclose(augmented[pivot][col], 0):
            raise ValueError("normal equation matrix is singular")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        pivot_value = augmented[col][col]
        for item in range(col, size + 1):
            augmented[col][item] /= pivot_value

        for row in range(size):
            if row == col:
                continue
            factor = augmented[row][col]
            for item in range(col, size + 1):
                augmented[row][item] -= factor * augmented[col][item]

    return [augmented[row][-1] for row in range(size)]


def evaluate_polynomial(coefficients: Sequence[float], x_value: float) -> float:
    return sum(coefficient * (x_value ** power) for power, coefficient in enumerate(coefficients))


def rmse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    if len(actual) != len(predicted):
        raise ValueError("actual and predicted values must have the same length")
    if not actual:
        raise ValueError("at least one value is required")
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual))


def loocv_rmse(x_values: Sequence[float], y_values: Sequence[float], degree: int) -> float:
    errors: list[float] = []
    for excluded in range(len(x_values)):
        train_x = [x for i, x in enumerate(x_values) if i != excluded]
        train_y = [y for i, y in enumerate(y_values) if i != excluded]
        coefficients = least_squares_polynomial(train_x, train_y, degree)
        predicted = evaluate_polynomial(coefficients, x_values[excluded])
        errors.append((predicted - y_values[excluded]) ** 2)
    return math.sqrt(sum(errors) / len(errors))


def pearson(x_values: Sequence[float], y_values: Sequence[float]) -> float:
    """Compute the Pearson correlation coefficient."""
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have the same length")
    if len(x_values) < 2:
        raise ValueError("at least two points are required")

    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_var = sum((x - x_mean) ** 2 for x in x_values)
    y_var = sum((y - y_mean) ** 2 for y in y_values)
    denominator = math.sqrt(x_var * y_var)
    if math.isclose(denominator, 0):
        raise ValueError("correlation is undefined for a constant sequence")
    return numerator / denominator


def recovery_rows(data: Iterable[DataPoint] = DATA) -> list[DataPoint]:
    return [row for row in data if 2020 <= row.year <= 2023]


def predict_by_recovery_segment(
    target_years: Iterable[int],
    metric: str,
    data: Iterable[DataPoint] = DATA,
) -> dict[int, float]:
    """Fit the 2020-2023 recovery segment and predict selected years."""
    rows = recovery_rows(data)
    x_values = [row.year - 2020 for row in rows]
    y_values = [float(getattr(row, metric)) for row in rows]
    slope, intercept = least_squares_line(x_values, y_values)
    return {year: slope * (year - 2020) + intercept for year in target_years}


def build_prediction_table(target_years: Iterable[int]) -> dict[int, dict[str, float]]:
    years = list(target_years)
    predictions = {
        "museums": predict_by_recovery_segment(years, "museums"),
        "visitors_million": predict_by_recovery_segment(years, "visitors_million"),
        "tourism_spending_100m_yuan": predict_by_recovery_segment(
            years,
            "tourism_spending_100m_yuan",
        ),
    }
    return {
        year: {
            metric: metric_predictions[year]
            for metric, metric_predictions in predictions.items()
        }
        for year in years
    }


def segmented_linear_predictions(
    years: Sequence[int],
    values: Sequence[float],
    break_year: int = 2020,
) -> tuple[list[float], tuple[float, float], tuple[float, float]]:
    """Fit separate least-squares lines before and after a structural break."""
    stable = [(year, value) for year, value in zip(years, values) if year < break_year]
    recovery = [(year, value) for year, value in zip(years, values) if year >= break_year]
    if len(stable) < 2 or len(recovery) < 2:
        raise ValueError("each segment needs at least two points")

    stable_slope, stable_intercept = least_squares_line(
        [year - stable[0][0] for year, _ in stable],
        [value for _, value in stable],
    )
    recovery_slope, recovery_intercept = least_squares_line(
        [year - break_year for year, _ in recovery],
        [value for _, value in recovery],
    )

    predictions = []
    for year in years:
        if year < break_year:
            predictions.append(stable_slope * (year - stable[0][0]) + stable_intercept)
        else:
            predictions.append(recovery_slope * (year - break_year) + recovery_intercept)
    return predictions, (stable_slope, stable_intercept), (recovery_slope, recovery_intercept)


def build_model_comparison_table(data: Sequence[DataPoint] = DATA) -> list[dict[str, object]]:
    """Compare full-period polynomial fits with segmented least squares."""
    years = [row.year for row in data]
    x_values = [year - years[0] for year in years]
    rows: list[dict[str, object]] = []

    for metric, label in METRIC_LABELS.items():
        values = [float(getattr(row, metric)) for row in data]
        linear = least_squares_polynomial(x_values, values, 1)
        quadratic = least_squares_polynomial(x_values, values, 2)
        segmented, stable_params, recovery_params = segmented_linear_predictions(years, values)
        model_outputs = [
            (
                "全周期线性",
                [evaluate_polynomial(linear, x) for x in x_values],
                loocv_rmse(x_values, values, 1),
                linear[1],
                "",
            ),
            (
                "全周期二次",
                [evaluate_polynomial(quadratic, x) for x in x_values],
                loocv_rmse(x_values, values, 2),
                "",
                "",
            ),
            (
                "分段线性",
                segmented,
                "",
                stable_params[0],
                recovery_params[0],
            ),
        ]
        for model, predictions, cv_rmse, stable_slope, recovery_slope in model_outputs:
            rows.append(
                {
                    "metric": label,
                    "model": model,
                    "rmse": rmse(values, predictions),
                    "loocv_rmse": cv_rmse,
                    "stable_slope": stable_slope,
                    "recovery_slope": recovery_slope,
                }
            )
    return rows


def build_counterfactual_gap_table(data: Sequence[DataPoint] = DATA) -> list[dict[str, object]]:
    """Use 2014-2019 stable trend as a counterfactual baseline for 2020-2023."""
    stable = [row for row in data if 2014 <= row.year <= 2019]
    shock_recovery = [row for row in data if 2020 <= row.year <= 2023]
    rows: list[dict[str, object]] = []

    for metric in ("visitors_million", "tourism_spending_100m_yuan"):
        slope, intercept = least_squares_line(
            [row.year - 2014 for row in stable],
            [float(getattr(row, metric)) for row in stable],
        )
        for row in shock_recovery:
            trend = slope * (row.year - 2014) + intercept
            actual = float(getattr(row, metric))
            rows.append(
                {
                    "metric": METRIC_LABELS[metric],
                    "year": row.year,
                    "actual": actual,
                    "stable_trend": trend,
                    "gap": actual - trend,
                    "actual_to_trend_ratio": actual / trend,
                }
            )
    return rows


def build_processed_feature_table(data: Sequence[DataPoint] = DATA) -> list[dict[str, object]]:
    """Build cleaned, indexed, and conversion-oriented features for reporting."""
    if not data:
        raise ValueError("data cannot be empty")

    base = data[0]
    rows: list[dict[str, object]] = []
    for row in data:
        rows.append(
            {
                "year": row.year,
                "stage": row.stage,
                "museums": row.museums,
                "visitors_million": row.visitors_million,
                "tourism_spending_100m_yuan": row.tourism_spending_100m_yuan,
                "museum_index": row.museums / base.museums * 100,
                "visitor_index": row.visitors_million / base.visitors_million * 100,
                "spending_index": row.tourism_spending_100m_yuan
                / base.tourism_spending_100m_yuan
                * 100,
                "visitors_per_museum_million": row.visitors_million / row.museums,
                "spending_per_visitor_yuan": row.tourism_spending_100m_yuan
                * 100
                / row.visitors_million,
                "spending_per_museum_100m_yuan": row.tourism_spending_100m_yuan
                / row.museums,
            }
        )
    return rows


def build_diff_table(data: Sequence[DataPoint] = DATA) -> list[dict[str, object]]:
    museums_diff = three_point_diff([row.museums for row in data])
    visitors_diff = three_point_diff([row.visitors_million for row in data])
    spending_diff = three_point_diff([row.tourism_spending_100m_yuan for row in data])
    return [
        {
            "year": row.year,
            "stage": row.stage,
            "museums": row.museums,
            "visitors_million": row.visitors_million,
            "tourism_spending_100m_yuan": row.tourism_spending_100m_yuan,
            "museums_diff": museums_diff[i],
            "visitors_diff": visitors_diff[i],
            "tourism_spending_diff": spending_diff[i],
        }
        for i, row in enumerate(data)
    ]


def correlation_summary(data: Sequence[DataPoint] = DATA) -> dict[str, float]:
    stable = [row for row in data if 2014 <= row.year <= 2019]
    return {
        "stable_museums_visitors": pearson(
            [row.museums for row in stable],
            [row.visitors_million for row in stable],
        ),
        "stable_museums_spending": pearson(
            [row.museums for row in stable],
            [row.tourism_spending_100m_yuan for row in stable],
        ),
        "full_museums_visitors": pearson(
            [row.museums for row in data],
            [row.visitors_million for row in data],
        ),
        "full_museums_spending": pearson(
            [row.museums for row in data],
            [row.tourism_spending_100m_yuan for row in data],
        ),
    }


def format_csv_value(value: object) -> object:
    if isinstance(value, float):
        return f"{value:.4f}" if abs(value) < 1 else f"{value:.1f}"
    return value


def write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(
            {key: format_csv_value(value) for key, value in row.items()}
            for row in rows
        )


def save_plots(output_dir: Path, data: Sequence[DataPoint] = DATA) -> None:
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    years = [row.year for row in data]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(years, [row.museums for row in data], marker="o", label="博物馆数量（个）")
    ax1.set_ylabel("博物馆数量（个）")
    ax1.axvline(2020, color="#d62728", linestyle="--", linewidth=1, label="2020 冲击")
    ax2 = ax1.twinx()
    ax2.plot(
        years,
        [row.tourism_spending_100m_yuan for row in data],
        marker="s",
        color="#2ca02c",
        label="国内旅游总花费（亿元）",
    )
    ax2.set_ylabel("国内旅游总花费（亿元）")
    fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.88))
    ax1.set_title("文化供给增长与旅游消费修复")
    ax1.set_xlabel("年份")
    fig.tight_layout()
    fig.savefig(output_dir / "trend_museums_spending.png", dpi=200)
    plt.close(fig)

    diff_rows = build_diff_table(data)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, [row["museums_diff"] for row in diff_rows], marker="o", label="博物馆年度增量")
    ax.plot(years, [row["visitors_diff"] for row in diff_rows], marker="s", label="游客年度变化")
    ax.axhline(0, color="#666666", linewidth=0.8)
    ax.axvline(2020, color="#d62728", linestyle="--", linewidth=1)
    ax.set_title("三点差分识别需求冲击与恢复")
    ax.set_xlabel("年份")
    ax.set_ylabel("边际变化（单位同原始指标 / 年）")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "diff_marginal_change.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    stable = [row for row in data if row.year <= 2019]
    shock = [row for row in data if row.year >= 2020]
    ax.scatter(
        [row.museums for row in stable],
        [row.visitors_million for row in stable],
        label="2014-2019",
    )
    ax.scatter(
        [row.museums for row in shock],
        [row.visitors_million for row in shock],
        label="2020-2023",
    )
    for row in data:
        ax.annotate(str(row.year), (row.museums, row.visitors_million), fontsize=8)
    ax.set_title("博物馆数量与国内游客相关性")
    ax.set_xlabel("博物馆数量（个）")
    ax.set_ylabel("国内游客（百万人次）")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "correlation_scatter.png", dpi=200)
    plt.close(fig)


def print_summary(predictions: dict[int, dict[str, float]]) -> None:
    print("三点差分关键读数：")
    diff_by_year = {row["year"]: row for row in build_diff_table()}
    print(f"  2020 年游客变化率：{diff_by_year[2020]['visitors_diff']:.1f} 百万人次/年")
    print(f"  2023 年游客变化率：{diff_by_year[2023]['visitors_diff']:.1f} 百万人次/年")

    print("\nPearson 相关系数：")
    for name, value in correlation_summary().items():
        print(f"  {name}: {value:.3f}")

    print("\n恢复段拟合预测：")
    for year, values in predictions.items():
        print(
            f"  {year}: 博物馆 {values['museums']:.1f} 个，"
            f"游客 {values['visitors_million']:.1f} 百万人次，"
            f"消费 {values['tourism_spending_100m_yuan']:.1f} 亿元"
        )

    print("\n模型比较关键结论：")
    comparison = build_model_comparison_table()
    for metric in ("国内游客", "旅游总花费"):
        rows = {row["model"]: row for row in comparison if row["metric"] == metric}
        print(
            f"  {metric}: 分段线性 RMSE {rows['分段线性']['rmse']:.1f}，"
            f"全周期线性 RMSE {rows['全周期线性']['rmse']:.1f}"
        )

    print("\n反事实缺口关键读数：")
    gaps = build_counterfactual_gap_table()
    for metric in ("国内游客", "旅游总花费"):
        rows = [row for row in gaps if row["metric"] == metric]
        first = next(row for row in rows if row["year"] == 2020)
        last = next(row for row in rows if row["year"] == 2023)
        print(
            f"  {metric}: 2020 年实际/平稳趋势 {first['actual_to_trend_ratio']:.1%}，"
            f"2023 年恢复到 {last['actual_to_trend_ratio']:.1%}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce numerical analysis for the course PPT.")
    parser.add_argument("--output-dir", default="outputs", help="directory for CSV and PNG results")
    parser.add_argument("--no-plots", action="store_true", help="skip matplotlib chart generation")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    prediction_rows = [
        {"year": year, **values}
        for year, values in build_prediction_table([2024, 2025, 2026]).items()
    ]
    write_csv(output_dir / "digital_economy_diff_results.csv", build_diff_table())
    write_csv(output_dir / "digital_economy_predictions.csv", prediction_rows)
    write_csv(output_dir / "digital_economy_model_comparison.csv", build_model_comparison_table())
    write_csv(output_dir / "digital_economy_counterfactual_gap.csv", build_counterfactual_gap_table())
    write_csv(output_dir / "digital_economy_processed_features.csv", build_processed_feature_table())
    if not args.no_plots:
        try:
            save_plots(output_dir)
        except ModuleNotFoundError as exc:
            if exc.name != "matplotlib":
                raise
            print(
                "未检测到 matplotlib，已跳过 PNG 图表生成；"
                "CSV 和文本结果已生成。可安装 matplotlib 后重新运行，"
                "或使用 --no-plots 显式跳过图表。",
                file=sys.stderr,
            )
    print_summary({int(row["year"]): {k: v for k, v in row.items() if k != "year"} for row in prediction_rows})


if __name__ == "__main__":
    main()
