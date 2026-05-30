# Repository Guidelines

## Project Structure & Module Organization

This is a Python data-science project for predicting traffic-accident mental damages from Taiwanese court JSON data. The workflow is organized as numbered scripts:

- `01_extract_rar.py`: extracts raw Judicial Yuan RAR archives.
- `02_build_dataset.py`: filters accident compensation cases and builds the first CSV dataset.
- `03_exploratory_analysis.py`: cleans data, encodes features, and writes `dataset_cleaned.csv`.
- `04_model_training.py`: trains/evaluates the Random Forest model and writes `models/rf_model.pkl`.
- `05_demo_app.py`: Streamlit demo app using the trained model.

Raw selected JSON files live in `Selected_JSON(原始訓練資料)/`. Generated or derived artifacts include `dataset_cleaned.csv`, `models/`, `.docx`, and `.pptx` reports.

## Build, Test, and Development Commands

Install runtime dependencies:

```bash
pip install pandas numpy scikit-learn streamlit joblib tqdm
```

Run the main workflow:

```bash
python 03_exploratory_analysis.py
python 04_model_training.py
streamlit run 05_demo_app.py
```

Use `python 01_extract_rar.py --years 2023-2025` only when the local archive paths and 7-Zip path are configured. Shared paths now live in `config.py` and default to project-relative locations; use environment overrides like `SOURCE_DIR`, `DEST_DIR`, and `SEVEN_ZIP` when data or tools live elsewhere.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Keep script names numbered to preserve pipeline order. Prefer `Path` for filesystem paths, constants in uppercase (`BASE_DIR`, `MODEL_DIR`), and snake_case for functions and variables. Preserve UTF-8 encoding because source comments, data paths, and UI labels include Chinese text.

## Testing Guidelines

There is no formal test suite yet. Before submitting changes, run the affected pipeline step and a Streamlit smoke test when app behavior changes. For data extraction changes, validate on a small subset first and confirm row counts, required columns, and representative parsed values before rebuilding the full dataset.

## Commit & Pull Request Guidelines

Git history currently only shows `init repo`, so no detailed commit convention is established. Use short, imperative commit messages such as `Add model training validation` or `Fix dataset path handling`. Pull requests should describe the changed workflow step, list regenerated artifacts, include key metrics when training changes (`MAE`, `R-squared`), and attach screenshots for Streamlit UI updates.

## Data & Configuration Notes

Avoid committing private raw archives or machine-specific absolute paths. Keep large generated files intentional, and document when `dataset_cleaned.csv` or `models/rf_model.pkl` has been regenerated.
