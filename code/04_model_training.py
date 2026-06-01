#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_model_training.py
進行機器學習模型訓練與評估
讀取：data/processed/dataset_cleaned.csv
產出：models/rf_model.pkl
對應期末專案 PPTX: 2. Modeling & 3. Results
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
import joblib

from config import CLEANED_DATASET_CSV, MODEL_DIR, MODEL_PATH


def real_money_mae_from_log(y_true_log, y_pred_log):
    """Compute MAE in NT dollars after converting log targets back to money."""
    y_true_real = np.expm1(y_true_log)
    y_pred_real = np.expm1(y_pred_log)
    return mean_absolute_error(y_true_real, y_pred_real)


def main():
    print("="*50)
    print("[執行] 模型建構與訓練 (Modeling)")
    print("="*50)

    # 1. 讀取清洗後的資料集
    if not CLEANED_DATASET_CSV.exists():
        print(f"[錯誤] 找不到清洗後的資料集: {CLEANED_DATASET_CSV}")
        return

    df = pd.read_csv(CLEANED_DATASET_CSV)
    print(f"讀取資料筆數: {len(df)}")

    # 2. 定義特徵 (X) 與目標變數 (y)
    # 我們不使用原本的絕對金額，而是使用 Log Transform 後的特徵來訓練，會更穩定
    # X 不包含 JID(流水號), 原始類別(Injury), 原始金額, 以及 Verdict_Total(總金額，因為總金額包含慰撫金，會造成 data leakage)
    drop_cols = [
        'JID', 'Year', 'Injury', 'Mental_Damage', 'Mental_Damage_log', 
        'Medical_Fee', 'Care_Fee', 'Work_Loss', 'Verdict_Total'
    ]
    
    # 實際使用的特徵 (X)
    X = df.drop(columns=drop_cols)
    # 我們預測 Log 後的慰撫金
    y_log = df['Mental_Damage_log']
    # 保留真實金額用來算最後的 Error
    y_real = df['Mental_Damage']

    print("\n[使用特徵清單]:")
    print(", ".join(X.columns.tolist()))

    # 3. 切割訓練集與測試集 (80% / 20%)
    # 使用 random_state 確保每次跑結果一樣 (可重現性)
    X_train, X_test, y_log_train, y_log_test, y_real_train, y_real_test = train_test_split(
        X, y_log, y_real, test_size=0.2, random_state=42
    )
    print(f"\n訓練集大小: {len(X_train)} 筆, 測試集大小: {len(X_test)} 筆")

    # 4. 基準模型 (Null Model)
    # 根據老師要求，我們需要一個 Null Model 供比較
    # 策略：以訓練集的「慰撫金平均值」作為預測值
    null_pred = np.full(shape=len(y_real_test), fill_value=y_real_train.mean())
    null_mae = mean_absolute_error(y_real_test, null_pred)
    print("\n" + "-"*40)
    print(f"基準模型 (Null Model) - 盲猜平均值")
    print(f"MAE (平均絕對誤差): {null_mae:,.0f} 元")
    print("-"*40)

    # 5. 固定參數隨機森林模型 (Fixed Random Forest Baseline)
    print("\n[執行] 訓練固定參數隨機森林模型 (Fixed Random Forest Baseline)...")
    fixed_rf = RandomForestRegressor(
        n_estimators=100, 
        max_depth=10, 
        min_samples_leaf=5,
        min_samples_split=2,
        max_features=1.0,
        random_state=42,
        n_jobs=-1 # 使用所有 CPU 核心
    )
    fixed_rf.fit(X_train, y_log_train)

    # 進行預測 (預測出來的是 log 值，需要轉回真實金額 np.expm1)
    fixed_pred_log = fixed_rf.predict(X_test)
    fixed_pred_real = np.expm1(fixed_pred_log)

    fixed_mae = mean_absolute_error(y_real_test, fixed_pred_real)
    fixed_r2 = r2_score(y_log_test, fixed_pred_log) # R2 用 log 算比較合理

    print("\n" + "-"*40)
    print(f"固定參數模型 (Fixed Random Forest)")
    print(f"MAE (平均絕對誤差): {fixed_mae:,.0f} 元")
    print(f"R-squared: {fixed_r2:.4f}")
    fixed_improvement = (null_mae - fixed_mae) / null_mae * 100
    print(f"比 Null Model 準確度提升: {fixed_improvement:.1f}%")
    print("-"*40)

    # 6. 使用 GridSearchCV 進行超參數調整
    print("\n[執行] GridSearchCV 超參數調整 (3-fold CV)...")
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [8, 10, None],
        "min_samples_leaf": [2, 5],
        "min_samples_split": [2, 5],
        "max_features": [0.7, 1.0],
    }
    scorer = make_scorer(real_money_mae_from_log, greater_is_better=False)
    grid_search = GridSearchCV(
        estimator=RandomForestRegressor(random_state=42, n_jobs=-1),
        param_grid=param_grid,
        scoring=scorer,
        cv=3,
        n_jobs=1,
        verbose=1,
    )
    grid_search.fit(X_train, y_log_train)

    rf = grid_search.best_estimator_
    cv_mae = -grid_search.best_score_

    print("\n最佳超參數 (Best Hyperparameters):")
    for key, value in grid_search.best_params_.items():
        print(f"{key}: {value}")
    print(f"交叉驗證 MAE (CV MAE): {cv_mae:,.0f} 元")

    # 7. 成效評估 (Results)
    rf_pred_log = rf.predict(X_test)
    rf_pred_real = np.expm1(rf_pred_log)
    rf_mae = mean_absolute_error(y_real_test, rf_pred_real)
    rf_r2 = r2_score(y_log_test, rf_pred_log)

    print("\n" + "-"*40)
    print(f"調參後模型 (Tuned Random Forest)")
    print(f"MAE (平均絕對誤差): {rf_mae:,.0f} 元")
    print(f"R-squared: {rf_r2:.4f}")

    improvement = (null_mae - rf_mae) / null_mae * 100
    print(f"➡️ 比 Null Model 準確度提升了 {improvement:.1f}%！ (Significant Improvement)")
    tuning_delta = fixed_mae - rf_mae
    delta_label = "降低" if tuning_delta >= 0 else "增加"
    print(f"相較固定參數 RF 的 MAE {delta_label}: {abs(tuning_delta):,.0f} 元")
    print("-"*40)

    # 8. 特徵重要性 (Feature Importance)
    print("\n[執行] 特徵重要性分析 (Feature Importance)...")
    importances = rf.feature_importances_
    # 將特徵與重要性配對並排序
    feat_imp = pd.DataFrame({
        'Feature': X.columns,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    print("\n前 5 大影響慰撫金判決的因素：")
    for i, row in feat_imp.head(5).iterrows():
        print(f"{row['Feature']:>20}: {row['Importance']:.4f}")

    # 9. 儲存模型
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    # 同時儲存模型和特徵欄位名稱，方便 Demo App 使用
    joblib.dump({'model': rf, 'features': X.columns.tolist()}, MODEL_PATH)
    print(f"\n[成功] 模型已儲存至：{MODEL_PATH}")
    print("="*50)

if __name__ == "__main__":
    main()
