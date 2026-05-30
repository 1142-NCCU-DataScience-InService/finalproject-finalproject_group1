# Repository Guidelines

## Project Structure & Module Organization

This is a Python data-science project for predicting mental damages in Taiwanese traffic-accident court cases. Keep the numbered workflow under `code/` and use `code/config.py` as the shared path contract.

- `code/01_extract_rar.py`: extracts Judicial Yuan RAR archives into month folders.
- `code/02_build_dataset.py`: filters traffic-accident damages cases, extracts regex-based features, writes the raw CSV, and copies matched JSON files.
- `code/03_exploratory_analysis.py`: cleans data, encodes features, creates log-transformed monetary fields, and writes `data/processed/dataset_cleaned.csv`.
- `code/04_model_training.py`: trains/evaluates the Random Forest model and writes `models/rf_model.pkl`.
- `code/05_demo_app.py`: Streamlit demo app using the trained model artifact.
- `tests/`: currently holds test scaffolding only; `tests/conftest.py` adds `code/` to `sys.path`.

Raw data defaults live under `data/raw/`: original archives in `OPENDATA-原稿/`, extracted files in `Extracted_OpenData/`, and matched case JSON in `Selected_JSON(原始訓練資料)/`. Processed CSV artifacts live under `data/processed/`; the current repo includes `dataset_cleaned.csv` but not necessarily `car_accident_dataset.csv`. Model artifacts live in `models/`; reports, slides, images, and other outputs live under `docs/`, `image/`, and `results/`.

## Build, Test, and Development Commands

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Run the full workflow from the repository root when raw or extracted data is available:

```bash
python3 code/01_extract_rar.py --years 2023-2025
python3 code/02_build_dataset.py
python3 code/03_exploratory_analysis.py
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

For the current checked-in state, the back half can be run directly because `data/processed/dataset_cleaned.csv` is present:

```bash
python3 code/04_model_training.py
streamlit run code/05_demo_app.py
```

Use extraction only when local archives and 7-Zip are available. Shared paths default to project-relative locations in `code/config.py`. Override with `SOURCE_DIR`, `DEST_DIR`, `SELECTED_DIR`, and `SEVEN_ZIP` when data or tools live elsewhere. For parser experiments, prefer environment overrides that point at a small temporary subset instead of rebuilding all extracted data.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Keep script names numbered to preserve pipeline order. Prefer `Path` for filesystem paths, constants in uppercase (`BASE_DIR`, `MODEL_DIR`), and snake_case for functions and variables. Preserve UTF-8 encoding because source comments, data paths, Streamlit labels, and court data include Chinese text.

Follow the local script style: small top-level helper functions, a `main()` entry point for CLI scripts, and `if __name__ == "__main__": main()` for executable workflow files. Import paths from `config.py` instead of reconstructing project paths or committing machine-specific absolute paths. When writing CSV outputs used by the course/report workflow, keep `encoding="utf-8-sig"` for Excel compatibility.

For court JSON ingestion, preserve the defensive encoding pattern (`utf-8`, `utf-8-sig`, then `cp950`) unless you have validated a narrower assumption against real files. Keep regex extraction changes conservative and document any new legal-term keyword assumptions near the pattern.

## Modeling & App Contracts

The modeling flow trains on log-transformed monetary features (`np.log1p`) and converts predictions back with `np.expm1`. Preserve the leakage guardrails in `code/04_model_training.py`: do not train on identifiers, raw target columns, or `Verdict_Total`, which can include the target amount. Keep `random_state=42` for reproducible train/test splits and model comparisons unless the change explicitly studies randomness.

`models/rf_model.pkl` is a `joblib` artifact containing `{"model": rf, "features": X.columns.tolist()}`. The Streamlit app builds its input dataframe from this saved feature list, so any feature engineering change in `code/03_exploratory_analysis.py` or `code/04_model_training.py` must be reflected in `code/05_demo_app.py` and should include updated metrics in README/docs.

Current training metrics from `data/processed/dataset_cleaned.csv` are approximately: Null Model MAE 494,720; Random Forest MAE 304,966; R-squared 0.4618. Recompute and update docs whenever model logic, data, or dependencies change.

## Testing Guidelines

There is no formal test suite yet. Before submitting changes, run the affected pipeline step and inspect the key outputs:

- Dataset-building changes: run against a small subset, then confirm row counts, required columns, and representative parsed values.
- Cleaning/feature changes: run `python3 code/03_exploratory_analysis.py` and verify `data/processed/dataset_cleaned.csv` shape and expected columns.
- Training changes: run `python3 code/04_model_training.py`, record `MAE`, `R-squared`, and feature importance changes, and confirm `models/rf_model.pkl` loads.
- Streamlit changes: run `streamlit run code/05_demo_app.py` and perform one prediction smoke test.

When adding automated tests, prefer `pytest` under `tests/` and focus first on `config.py` path resolution, regex feature extraction, preprocessing column contracts, and model/app feature-schema compatibility.

## Commit & Pull Request Guidelines

Use short, imperative commit messages such as `Add model training validation` or `Fix dataset path handling`. Pull requests should describe the changed workflow step, list regenerated artifacts, include key metrics when training changes (`MAE`, `R-squared`), and attach screenshots for Streamlit UI updates.

## Data & Configuration Notes

Avoid committing private raw archives or machine-specific absolute paths. `.gitignore` excludes the largest raw archive/extraction directories, but contributors should still review generated data before committing. Keep large generated files intentional, and document when `data/processed/car_accident_dataset.csv`, `data/processed/dataset_cleaned.csv`, `models/rf_model.pkl`, report documents, or slide decks have been regenerated.

`code/02_build_dataset.py` copies matched source JSON into `SELECTED_DIR` by default. Treat those files as data artifacts: do not rename their source-derived IDs casually, and avoid committing expanded raw selections unless the project explicitly needs them.
