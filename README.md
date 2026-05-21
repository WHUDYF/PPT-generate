# PPT-generate

Generated presentation materials and supporting documents.

## Contents

### Presentations

- `presentations/group_meeting_mechanism_attribution_2026_05_16_20260519_114907.pptx`
- `presentations/digital_economy_numerical_20260519_113555.pptx`
- `presentations/digital_economy_numerical_segmented_20260521.pptx`
- `presentations/digital_economy_numerical_corrected_20260522.pptx`

### PPT Master Projects

- `projects/digital_economy_numerical_v2_ppt169_20260522/`

### Documents

- `documents/学号-姓名-数值技术.docx`
- `documents/学号-姓名-数值技术.pdf`
- `documents/数值技术报告修改补充.md`

### Sources

- `sources/AI_for_EDA赋能芯片设计职业发展.md`

### Numerical Analysis Code

- `scripts/digital_economy_numerical.py`

Run the code used by `presentations/digital_economy_numerical_20260519_113555.pptx`:

```bash
python scripts/digital_economy_numerical.py --output-dir outputs/digital_economy
```

If `matplotlib` is unavailable and only CSV/text results are needed:

```bash
python scripts/digital_economy_numerical.py --output-dir outputs/digital_economy --no-plots
```

The script exports finite-difference results, recovery-segment predictions, and optional PNG charts.
It also exports segmented least-squares model comparison and counterfactual gap CSV files:

- `outputs/digital_economy/digital_economy_model_comparison.csv`
- `outputs/digital_economy/digital_economy_counterfactual_gap.csv`
- `outputs/digital_economy/digital_economy_processed_features.csv`

## Notes

The `学号-姓名-数值技术` filenames are placeholders and should be renamed before course submission if personal information is required.
