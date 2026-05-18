#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_model_training.py
進行機器學習模型訓練與評估
對應期末專案 PPTX: 2. Modeling & 3. Results
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import os
from pathlib import Path

from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

BASE_DIR = Path(r"e:\AI_程式開發\Judge_data")
INPUT_CSV = BASE_DIR / "dataset_cleaned.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

def main():
    print("="*50)
    print("[執行] 模型建構與訓練 (Modeling)")
    print("="*50)

    # 1. 讀取清洗後的資料集
    df = pd.read_csv(INPUT_CSV)
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

    # 5. 訓練隨機森林模型 (Random Forest)
    print("\n[執行] 訓練隨機森林迴歸模型 (Random Forest)...")
    # 設定一些超參數來防止 Overfitting
    rf = RandomForestRegressor(
        n_estimators=100, 
        max_depth=10, 
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1 # 使用所有 CPU 核心
    )
    rf.fit(X_train, y_log_train)

    # 進行預測 (預測出來的是 log 值，需要轉回真實金額 np.expm1)
    rf_pred_log = rf.predict(X_test)
    rf_pred_real = np.expm1(rf_pred_log)

    # 6. 成效評估 (Results)
    rf_mae = mean_absolute_error(y_real_test, rf_pred_real)
    rf_r2 = r2_score(y_log_test, rf_pred_log) # R2 用 log 算比較合理

    print("\n" + "-"*40)
    print(f"機器學習模型 (Random Forest)")
    print(f"MAE (平均絕對誤差): {rf_mae:,.0f} 元")
    print(f"R-squared: {rf_r2:.4f}")
    
    improvement = (null_mae - rf_mae) / null_mae * 100
    print(f"➡️ 比 Null Model 準確度提升了 {improvement:.1f}%！ (Significant Improvement)")
    print("-"*40)

    # 7. 特徵重要性 (Feature Importance)
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

    # 8. 儲存模型
    model_path = MODEL_DIR / "rf_model.pkl"
    # 同時儲存模型和特徵欄位名稱，方便 Demo App 使用
    joblib.dump({'model': rf, 'features': X.columns.tolist()}, model_path)
    print(f"\n[成功] 模型已儲存至：{model_path}")
    print("="*50)

if __name__ == "__main__":
    main()
