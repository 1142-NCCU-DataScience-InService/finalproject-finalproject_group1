#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_build_dataset.py
從解壓縮後的裁判書中，篩選「車禍損害賠償」案件並擷取特徵。
產出：data/processed/car_accident_dataset.csv
"""

import os
import json
import re
import csv
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import time

from config import DEST_DIR, RAW_DATASET_CSV, SELECTED_DIR

# ─────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────
SOURCE_DIR = DEST_DIR
OUTPUT_CSV = RAW_DATASET_CSV
# [新增] 存放精選裁判書 JSON 的地方
COPY_MATCHED_FILES = True  # 是否要複製原始檔

# 篩選條件
TARGET_TITLE = "損害賠償"
KEYWORDS = ["車禍", "交通事故", "道路交通"]

# 擷取正則表達式
def find_money(text, patterns):
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                # 移除非數字字元
                val = re.sub(r"[^0-9]", "", m.group(1))
                return int(val)
            except: pass
    return None

def extract_features(rec):
    full = rec.get("JFULL", "")
    title = rec.get("JTITLE", "")
    
    # 1. 篩選：案由必須包含損害賠償
    if TARGET_TITLE not in title:
        return None
    
    # 2. 篩選：內文必須包含車禍關鍵字
    if not any(k in full for k in KEYWORDS):
        return None

    # 3. 擷取：精神慰撫金 (y)
    mental = find_money(full, [
        r"精神(?:上)?慰撫金[^，。；\d（(]{0,20}?([0-9,，]+)\s*元",
        r"非財產上損害[^，。；\d（(]{0,20}?([0-9,，]+)\s*元",
        r"慰撫金[^，。；\d（(]{0,15}?([0-9,，]+)\s*元",
    ])
    
    if not mental: return None # 沒抓到慰撫金的案子可能不是判決主體，跳過

    # 4. 擷取：判決給付金額
    verdict = find_money(full, [
        r"被告(?:應|須)給付原告[^。]{0,60}?([0-9,，]{4,})\s*元",
        r"給付原告[^。，]{0,30}?([0-9,，]{4,})\s*元",
    ])

    # 5. 擷取：醫療費
    medical = find_money(full, [r"醫療費(?:用)?[^，。；\d（(]{0,15}?([0-9,，]+)\s*元"])
    
    # 6. 擷取：看護費
    care = find_money(full, [r"看護費(?:用)?[^，。；\d（(]{0,15}?([0-9,，]+)\s*元"])
    
    # 7. 擷取：工作損失 (勞動能力減損)
    work_loss = find_money(full, [r"(?:勞動能力|工作)損失[^，。；\d（(]{0,15}?([0-9,，]+)\s*元"])

    # 8. 擷取：過失比例 (%)
    fault_ratio = 0
    m_fault = re.search(r"與有過失[^，。]{0,30}(\d+(?:\.\d+)?)\s*(?:%|百分之)", full)
    if m_fault:
        try: fault_ratio = float(m_fault.group(1))
        except: pass

    # 9. 傷亡類型
    if re.search(r"死亡|往生|殞命|不治", full): 
        injury = "死亡"
    elif re.search(r"重傷|截肢|植物人", full):  
        injury = "重傷"
    else:                                         
        injury = "傷害"

    # 10. 酒駕
    drunk = 1 if re.search(r"酒駕|酒後駕車|飲酒.*駕", full) else 0

    court = rec.get("JID", "").split(",")[0]
    yr = rec.get("JYEAR", "")
    
    return {
        "JID": rec.get("JID"),
        "Court": court,
        "Year": yr,
        "Injury": injury,
        "Drunk": drunk,
        "Medical_Fee": medical or 0,
        "Care_Fee": care or 0,
        "Work_Loss": work_loss or 0,
        "Fault_Ratio": fault_ratio,
        "Verdict_Total": verdict or 0,
        "Mental_Damage": mental  # 目標變數
    }

def process_file(jf):
    for enc in ("utf-8", "utf-8-sig", "cp950"):
        try:
            with open(jf, 'r', encoding=enc) as f:
                rec = json.load(f)
            break
        except:
            rec = None
    
    if not rec: return None
    return extract_features(rec)

# ─────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────

def main():
    print(f"開始掃描目錄：{SOURCE_DIR}")

    # 取得所有待處理月份資料夾
    month_dirs = sorted([d for d in SOURCE_DIR.iterdir() if d.is_dir()]) if SOURCE_DIR.exists() else []
    
    fallback_mode = False
    selected_jsons = []
    if not month_dirs:
        if SELECTED_DIR.exists():
            selected_jsons = list(SELECTED_DIR.glob("*.json"))
            if selected_jsons:
                print(f"[提示] 未發現解壓縮月份目錄，啟用 Fallback 模式：直接從精選資料夾 {SELECTED_DIR} 讀取 {len(selected_jsons)} 筆 JSON。")
                fallback_mode = True
            else:
                print(f"[錯誤] 找不到解壓縮後的資料目錄 {SOURCE_DIR}，且精選資料夾 {SELECTED_DIR} 亦無 JSON 檔案。")
                return
        else:
            print(f"[錯誤] 找不到解壓縮後的資料目錄 {SOURCE_DIR}，且精選資料夾 {SELECTED_DIR} 不存在。")
            return
    
    fieldnames = [
        "JID", "Court", "Year", "Injury", "Drunk", 
        "Medical_Fee", "Care_Fee", "Work_Loss", 
        "Fault_Ratio", "Verdict_Total", "Mental_Damage"
    ]

    if COPY_MATCHED_FILES and not fallback_mode:
        SELECTED_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        total_found = 0
        import shutil
        
        if fallback_mode:
            print("正在處理精選 JSON 檔案...", end="", flush=True)
            count = 0
            for jf in selected_jsons:
                res = process_file(jf)
                if res:
                    writer.writerow(res)
                    count += 1
            total_found = count
            print(f" 成功讀取並匯出 {count} 筆。")
            csvfile.flush()
        else:
            for m_dir in month_dirs:
                print(f"正在處理：{m_dir.name}...", end="", flush=True)
                
                json_files = list(m_dir.rglob("*.json"))
                count = 0
                
                for jf in json_files:
                    res = process_file(jf)
                    if res:
                        writer.writerow(res)
                        count += 1
                        
                        # [新增] 複製檔案邏輯
                        if COPY_MATCHED_FILES:
                            # 檔名格式：法院_年度_字號_編號.json
                            # JID 格式通常是 "法院,案由,年度,字號,編號"
                            safe_jid = res["JID"].replace(",", "_")
                            target_path = SELECTED_DIR / f"{safe_jid}.json"
                            if not target_path.exists():
                                shutil.copy2(jf, target_path)
                
                total_found += count
                print(f" 找到 {count} 筆。")
                csvfile.flush() 

    print(f"\n完成！共擷取 {total_found} 筆有效案件，儲存至：{OUTPUT_CSV}")

if __name__ == "__main__":
    main()
