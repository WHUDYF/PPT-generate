import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.digital_economy_numerical import (
    DATA,
    build_counterfactual_gap_table,
    build_model_comparison_table,
    build_processed_feature_table,
    build_prediction_table,
    main,
    pearson,
    three_point_diff,
)


class DigitalEconomyNumericalTest(unittest.TestCase):
    def test_three_point_diff_captures_tourism_shock_and_recovery(self):
        visitors = [row.visitors_million for row in DATA]

        diff = three_point_diff(visitors)

        year_to_diff = {row.year: value for row, value in zip(DATA, diff)}
        self.assertAlmostEqual(year_to_diff[2020], -1380.0, places=1)
        self.assertAlmostEqual(year_to_diff[2023], 2361.0, places=1)

    def test_pearson_matches_stage_correlation_in_report(self):
        stable = [row for row in DATA if 2014 <= row.year <= 2019]
        all_years = DATA

        stable_corr = pearson(
            [row.museums for row in stable],
            [row.visitors_million for row in stable],
        )
        full_corr = pearson(
            [row.museums for row in all_years],
            [row.visitors_million for row in all_years],
        )

        self.assertAlmostEqual(stable_corr, 0.988, places=3)
        self.assertAlmostEqual(full_corr, -0.175, places=3)

    def test_recovery_segment_predictions_match_presentation_values(self):
        predictions = build_prediction_table([2024, 2025, 2026])

        self.assertAlmostEqual(predictions[2024]["museums"], 7392.5, places=1)
        self.assertAlmostEqual(predictions[2024]["visitors_million"], 4716.5, places=1)
        self.assertAlmostEqual(predictions[2024]["tourism_spending_100m_yuan"], 48211.9, places=1)
        self.assertAlmostEqual(predictions[2026]["museums"], 8383.3, places=1)
        self.assertAlmostEqual(predictions[2026]["visitors_million"], 5780.5, places=1)
        self.assertAlmostEqual(predictions[2026]["tourism_spending_100m_yuan"], 62570.6, places=1)

    def test_model_comparison_supports_segmented_least_squares_choice(self):
        comparison = build_model_comparison_table()

        visitors = {
            row["model"]: row
            for row in comparison
            if row["metric"] == "国内游客"
        }
        spending = {
            row["model"]: row
            for row in comparison
            if row["metric"] == "旅游总花费"
        }

        self.assertAlmostEqual(visitors["分段线性"]["rmse"], 432.8, places=1)
        self.assertLess(
            visitors["分段线性"]["rmse"],
            visitors["全周期线性"]["rmse"],
        )
        self.assertLess(
            spending["分段线性"]["rmse"],
            spending["全周期线性"]["rmse"],
        )
        self.assertGreater(
            visitors["全周期二次"]["loocv_rmse"],
            visitors["全周期线性"]["loocv_rmse"],
        )

    def test_counterfactual_gap_table_quantifies_recovery_against_stable_trend(self):
        gaps = build_counterfactual_gap_table()

        visitor_2020 = next(
            row for row in gaps
            if row["metric"] == "国内游客" and row["year"] == 2020
        )
        spending_2023 = next(
            row for row in gaps
            if row["metric"] == "旅游总花费" and row["year"] == 2023
        )

        self.assertAlmostEqual(visitor_2020["actual_to_trend_ratio"], 0.4442, places=4)
        self.assertAlmostEqual(visitor_2020["gap"], -3602.5, places=1)
        self.assertAlmostEqual(spending_2023["actual_to_trend_ratio"], 0.6242, places=4)
        self.assertAlmostEqual(spending_2023["gap"], -29578.7, places=1)

    def test_processed_feature_table_constructs_indices_and_conversion_metrics(self):
        features = build_processed_feature_table()

        row_2019 = next(row for row in features if row["year"] == 2019)
        row_2023 = next(row for row in features if row["year"] == 2023)

        self.assertAlmostEqual(row_2019["museum_index"], 140.3, places=1)
        self.assertAlmostEqual(row_2019["visitors_per_museum_million"], 1.170, places=3)
        self.assertAlmostEqual(row_2019["spending_per_visitor_yuan"], 953.2, places=1)
        self.assertEqual(row_2019["stage"], "高点")

        self.assertAlmostEqual(row_2023["museum_index"], 186.8, places=1)
        self.assertAlmostEqual(row_2023["spending_index"], 162.1, places=1)
        self.assertAlmostEqual(row_2023["spending_per_visitor_yuan"], 1004.6, places=1)
        self.assertEqual(row_2023["stage"], "修复")

    def test_cli_still_writes_csv_when_matplotlib_is_unavailable(self):
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            with patch("sys.argv", ["digital_economy_numerical.py", "--output-dir", str(output_dir)]):
                main()

            self.assertTrue((output_dir / "digital_economy_diff_results.csv").exists())
            self.assertTrue((output_dir / "digital_economy_predictions.csv").exists())
            self.assertTrue((output_dir / "digital_economy_model_comparison.csv").exists())
            self.assertTrue((output_dir / "digital_economy_counterfactual_gap.csv").exists())
            self.assertTrue((output_dir / "digital_economy_processed_features.csv").exists())

    def test_prediction_csv_uses_report_friendly_rounding(self):
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            with patch(
                "sys.argv",
                ["digital_economy_numerical.py", "--output-dir", str(output_dir), "--no-plots"],
            ):
                main()

            prediction_csv = (output_dir / "digital_economy_predictions.csv").read_text(
                encoding="utf-8-sig",
            )
            self.assertIn("2025,7887.9,5248.5,55391.3", prediction_csv)
            self.assertNotIn("55391.289999", prediction_csv)


if __name__ == "__main__":
    unittest.main()
