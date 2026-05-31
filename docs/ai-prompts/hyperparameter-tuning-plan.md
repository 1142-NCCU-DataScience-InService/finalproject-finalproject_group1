# Add Bounded Random Forest Hyperparameter Tuning

## Summary

Add real hyperparameter tuning to the existing modeling workflow while preserving the current script contract: `code/04_model_training.py` still reads `data/processed/dataset_cleaned.csv` and writes `models/rf_model.pkl` with the same schema, `{"model": rf, "features": X.columns.tolist()}`. The Streamlit app should continue loading the artifact without changes.

Use a compact `GridSearchCV` so the script finds the best parameters within an explicit bounded grid, instead of relying on hand-picked common values. Keep runtime targeted around three minutes by limiting the grid and using 3-fold CV.

## Key Changes

- Clean up the current mismatch first:
  - Remove unused imports such as `KFold` if no longer needed.
  - Keep `GridSearchCV` only once it is actually used.
  - Update README wording so it describes the tuned workflow instead of fixed-only RF parameters.
- Preserve the current feature/target setup:
  - Keep the same `drop_cols`.
  - Keep training target as `Mental_Damage_log`.
  - Keep final predictions converted back with `np.expm1`.
  - Do not change `models/rf_model.pkl` structure or feature names.
- Add a fixed Random Forest baseline before tuning:
  - Train/evaluate the current hand-picked model:
    - `n_estimators=100`
    - `max_depth=10`
    - `min_samples_leaf=5`
    - `min_samples_split=2`
    - `max_features=1.0`
    - `random_state=42`
    - `n_jobs=-1`
  - Print its test MAE and log-space R-squared for comparison.
- Add bounded `GridSearchCV` tuning:
  - Use `cv=3`.
  - Use `RandomForestRegressor(random_state=42, n_jobs=-1)`.
  - Use this compact grid:

    ```python
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [8, 10, None],
        "min_samples_leaf": [2, 5],
        "min_samples_split": [2, 5],
        "max_features": [0.7, 1.0],
    }
    ```

  - This is 48 candidates, 144 CV fits, and includes the current model configuration.
- Use a scorer aligned with the reported metric:
  - Define a custom scorer that receives log-space `y_true` / `y_pred`, converts both with `np.expm1`, and computes real-money MAE.
  - Use `make_scorer(..., greater_is_better=False)` so GridSearchCV minimizes real-money MAE.
  - Report the best CV MAE in NT dollars.
- Final model behavior:
  - Evaluate the tuned model once on the held-out test set.
  - Print:
    - Null Model MAE
    - Fixed RF MAE / R-squared
    - Tuned RF best params
    - Tuned RF CV MAE
    - Tuned RF test MAE / R-squared
    - Tuned top 5 feature importances
  - Save the CV-selected tuned model to `models/rf_model.pkl`.
  - Do not choose between fixed and tuned models based on test-set performance, because that would leak the test set into model selection.

## Documentation Updates

- README modeling section should say the final model uses `GridSearchCV` with 3-fold CV over a compact Random Forest grid.
- Replace the fixed hyperparameter bullet with:
  - the search grid,
  - the selected best parameters from the actual run,
  - the updated MAE / R-squared,
  - and whether tuning improved over the fixed RF baseline.
- Keep the artifact description unchanged: `{"model": rf, "features": X.columns.tolist()}`.
- If metrics change, also update any README text that says the model MAE is about 30 萬元.

## Test Plan

- Run:

  ```bash
  python3 code/04_model_training.py
  ```

- Confirm runtime is roughly within the three-minute target.
- Confirm output includes baseline RF, tuned RF, best parameters, and feature importance.
- Confirm `models/rf_model.pkl` loads with:
  - keys `model` and `features`,
  - the same number of feature columns as the training dataframe,
  - a model that can predict from a one-row dataframe built with the saved feature list.
- Run a Streamlit smoke test:

  ```bash
  uv run streamlit run code/05_demo_app.py
  ```

  Verify the app loads the regenerated artifact and can make one prediction.

## Assumptions

- "Best hyperparameters" means best within the bounded CV grid, not a global exhaustive search over all possible RF settings.
- Tuning should become the normal training path, not an optional CLI flag.
- The current train/test split and `random_state=42` remain fixed for comparability.
- No new model artifact format, CLI interface, or app input schema should be introduced.
