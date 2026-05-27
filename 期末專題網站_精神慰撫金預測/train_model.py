"""
重新訓練 Random Forest 模型（使用本地 dataset_cleaned.csv）。
獨立於原始程式碼，所有路徑皆相對化。

執行：
    python train_model.py
"""
import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from config import DATASET_CSV, MODEL_PATH

sys.stdout.reconfigure(encoding="utf-8")


def main():
    print("=" * 50)
    print("[執行] 模型訓練 - Random Forest Regressor")
    print("=" * 50)

    if not DATASET_CSV.exists():
        print(f"[錯誤] 找不到資料集：{DATASET_CSV}")
        print("請先把 dataset_cleaned.csv 複製到 data/ 資料夾下。")
        return

    df = pd.read_csv(DATASET_CSV)
    print(f"讀取資料筆數: {len(df)}")

    # 特徵與目標
    drop_cols = [
        "JID", "Year", "Injury", "Mental_Damage", "Mental_Damage_log",
        "Medical_Fee", "Care_Fee", "Work_Loss", "Verdict_Total",
    ]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y_log = df["Mental_Damage_log"]
    y_real = df["Mental_Damage"]

    # 切資料
    X_train, X_test, y_log_train, y_log_test, y_real_train, y_real_test = train_test_split(
        X, y_log, y_real, test_size=0.2, random_state=42
    )
    print(f"訓練集: {len(X_train)} 筆 / 測試集: {len(X_test)} 筆")

    # Null model
    null_pred = np.full(len(y_real_test), y_real_train.mean())
    null_mae = mean_absolute_error(y_real_test, null_pred)
    print(f"\nNull Model MAE: {null_mae:,.0f} 元")

    # Random Forest
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_log_train)

    pred_log = rf.predict(X_test)
    pred_real = np.expm1(pred_log)
    rf_mae = mean_absolute_error(y_real_test, pred_real)
    rf_r2 = r2_score(y_log_test, pred_log)

    print(f"Random Forest MAE: {rf_mae:,.0f} 元")
    print(f"R-squared: {rf_r2:.4f}")
    print(f"進步幅度: {(null_mae - rf_mae) / null_mae * 100:.1f}%")

    # Feature importance
    feat_imp = pd.DataFrame({
        "Feature": X.columns,
        "Importance": rf.feature_importances_,
    }).sort_values("Importance", ascending=False)
    print("\n前 5 大重要特徵：")
    for _, row in feat_imp.head(5).iterrows():
        print(f"  {row['Feature']:>20}: {row['Importance']:.4f}")

    joblib.dump({"model": rf, "features": X.columns.tolist()}, MODEL_PATH)
    print(f"\n[成功] 模型儲存至：{MODEL_PATH}")


if __name__ == "__main__":
    main()
