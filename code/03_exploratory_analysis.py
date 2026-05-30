#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_exploratory_analysis.py
進行資料清洗、探索性分析 (EDA) 與特徵工程
讀取：data/processed/car_accident_dataset.csv
產出：data/processed/dataset_cleaned.csv
對應期末專案 PPTX: 1. Input
"""

import pandas as pd
import numpy as np

import sys
sys.stdout.reconfigure(encoding='utf-8')

from config import CLEANED_DATASET_CSV, RAW_DATASET_CSV

# 設定路徑
INPUT_CSV = RAW_DATASET_CSV
OUTPUT_CSV = CLEANED_DATASET_CSV

def main():
    print("="*50)
    print("[執行] 車禍損害賠償 - 資料清洗與探索性分析 (EDA)")
    print("="*50)

    # 1. 讀取資料
    if not INPUT_CSV.exists():
        print(f"[錯誤] 找不到資料集: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    print(f"[成功] 成功讀取原始資料集：共 {len(df)} 筆案件")

    # 2. 處理缺失值 (Missing Data)
    print("\n[執行] 處理缺失值 (Handle missing data)...")
    fee_columns = ['Medical_Fee', 'Care_Fee', 'Work_Loss']
    for col in fee_columns:
        # 將缺失的金額補 0 (視為原告未請求此項目)
        df[col] = df[col].fillna(0)
    
    # 針對目標變數 (Mental_Damage)，如果有缺失則整筆刪除，因為無法訓練
    initial_len = len(df)
    df = df.dropna(subset=['Mental_Damage'])
    print(f"  -> 移除了 {initial_len - len(df)} 筆目標變數缺失的無效資料")

    # 3. 處理異常值 (Outliers)
    print("\n[執行] 處理異常值 (Outliers)...")
    # 觀察發現有些金額可能因為擷取錯誤高達幾百億，或是 0 元
    # 我們設定一個合理的範圍：精神慰撫金應在 1萬 ~ 1千萬 之間
    initial_len = len(df)
    df = df[(df['Mental_Damage'] >= 10000) & (df['Mental_Damage'] <= 10000000)]
    print(f"  -> 移除了 {initial_len - len(df)} 筆精神慰撫金異常(過高或過低)的案件")

    # 同理處理醫療費等，設定上限 (如不超過 5000萬)
    for col in fee_columns:
        df = df[df[col] <= 50000000]

    # 肇責比例 (Fault_Ratio) 必須在 0~100 之間
    df['Fault_Ratio'] = df['Fault_Ratio'].clip(0, 100)

    # 4. 特徵編碼 (Encoding)
    print("\n[執行] 類別特徵編碼 (Categorical Encoding)...")
    # 將傷亡類型 (Injury) 轉為 Ordinal Encoding (順序編碼)，因為嚴重度有差別
    injury_mapping = {'死亡': 3, '重傷': 2, '傷害': 1, '未知': 0}
    df['Injury_Level'] = df['Injury'].map(injury_mapping).fillna(0)
    
    # 使用 One-Hot Encoding 處理法院 (Court)，以捕捉地區差異
    df = pd.get_dummies(df, columns=['Court'], drop_first=True)

    # 5. 資料基本統計 (EDA)
    print("\n=== 資料分布摘要 ===")
    print(f"最終有效樣本數: {len(df)} 筆")
    print(f"\n【傷亡程度分佈】")
    print(df['Injury'].value_counts())
    
    print(f"\n【精神慰撫金 (目標變數) 統計】")
    pd.options.display.float_format = '{:,.0f}'.format
    print(df['Mental_Damage'].describe()[['min', '25%', '50%', 'mean', '75%', 'max']])

    print(f"\n【有無酒駕分佈】")
    print(df['Drunk'].value_counts().rename(index={0: '未酒駕', 1: '有酒駕'}))

    # 6. 特徵縮放 (Scale value)
    print("\n[執行] 特徵縮放 (Scale value)...")
    # 為了避免因為金額絕對值太大(動輒百萬)影響模型，我們對金額進行 Log1p 轉換 (Log(x+1))
    # 這樣符合老師 PPT 要求 Scale value
    scale_cols = ['Medical_Fee', 'Care_Fee', 'Work_Loss', 'Mental_Damage']
    for col in scale_cols:
        df[f'{col}_log'] = np.log1p(df[col])
    print("  -> 已完成金額特徵之對數轉換 (Log Transform)")

    # 7. 儲存清洗後的資料集
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\n[成功] 清洗完成！乾淨資料已儲存至：{OUTPUT_CSV}")
    print("="*50)

if __name__ == "__main__":
    main()
