#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_extract_rar.py
裁判書開放資料解壓縮工具
將 F:/OPENDATA-原稿 的 RAR 檔解壓縮到 H:/Extracted_OpenData

使用方式:
  python 01_extract_rar.py                      # 互動選單
  python 01_extract_rar.py --years 2023-2025    # 只解壓縮特定年份
  python 01_extract_rar.py --all                # 全部解壓縮
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# ─────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────
SEVEN_ZIP  = r"C:\Program Files\7-Zip\7z.exe"
SOURCE_DIR = Path(r"F:\OPENDATA-原稿")
DEST_DIR   = Path(r"H:\Extracted_OpenData")

# ─────────────────────────────────────────────
# 工具函式
# ─────────────────────────────────────────────

def check_env():
    """環境檢查"""
    ok = True
    if not Path(SEVEN_ZIP).exists():
        print(f"[ERROR] 找不到 7-Zip：{SEVEN_ZIP}")
        ok = False
    if not SOURCE_DIR.exists():
        print(f"[ERROR] 來源目錄不存在：{SOURCE_DIR}")
        ok = False
    return ok


def get_rar_list(year_start: int = None, year_end: int = None) -> list[Path]:
    """列出符合年份條件的 RAR 檔（依西元年 YYYY 過濾）"""
    rars = sorted(SOURCE_DIR.glob("*.rar"))
    if year_start is None and year_end is None:
        return rars

    result = []
    for r in rars:
        stem = r.stem[:6]          # 取前6碼 YYYYMM
        if not stem.isdigit():
            continue
        year = int(stem[:4])
        if year_start and year < year_start:
            continue
        if year_end and year > year_end:
            continue
        result.append(r)
    return result


def extract_one(rar: Path, dest: Path) -> bool:
    """用 7-Zip 解壓一個 RAR 到目標目錄（保留子目錄結構）"""
    dest.mkdir(parents=True, exist_ok=True)
    cmd = [SEVEN_ZIP, "x", str(rar), f"-o{dest}", "-y", "-aoa"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────

def run_extraction(rars: list[Path], skip_existing: bool = True):
    """執行解壓縮，並顯示進度
    skip_existing=True：若目標資料夾已存在且有 JSON 檔，則跳過（斷點續傳）
    """
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False
        print("[提示] 安裝 tqdm 可顯示進度條：pip install tqdm")

    # ── 預先過濾：已解壓的月份只解 Update 版 ──
    to_do   = []
    skipped = []
    seen_months = {}   # stem -> list of rars

    for rar in rars:
        stem = rar.stem[:6]   # YYYYMM
        seen_months.setdefault(stem, []).append(rar)

    for stem, month_rars in sorted(seen_months.items()):
        dest = DEST_DIR / stem
        json_count = len(list(dest.rglob("*.json"))) if dest.exists() else 0
        if skip_existing and json_count > 1000:
            skipped.append(stem)
            print(f"  [SKIP] {stem}（已有 {json_count:,} 個 JSON，跳過）")
        else:
            # 同月份若有多個版本，只取最新（檔名含日期最大）
            latest = sorted(month_rars)[-1]
            to_do.append(latest)

    print(f"\n跳過已解壓：{len(skipped)} 個月份")
    print(f"即將解壓  ：{len(to_do)} 個 RAR\n")

    if not to_do:
        print("所有月份均已解壓完成！")
        return

    total_size = sum(r.stat().st_size for r in to_do)
    print(f"目標目錄：{DEST_DIR}，總大小：{human_size(total_size)}\n")

    ok_count = 0
    fail_list = []

    iterator = tqdm(to_do, unit="rar") if use_tqdm else to_do
    for rar in iterator:
        stem = rar.stem[:6]
        dest = DEST_DIR / stem
        if not use_tqdm:
            print(f"  解壓中：{rar.name} → {dest}")

        success = extract_one(rar, dest)
        if success:
            ok_count += 1
        else:
            fail_list.append(rar.name)
            if not use_tqdm:
                print(f"  [FAIL] {rar.name}")

    print(f"\n完成！成功 {ok_count}/{len(to_do)} 個。")
    if fail_list:
        print("以下檔案解壓失敗：")
        for f in fail_list:
            print(f"  - {f}")


def interactive_menu():
    """互動選單"""
    print("=" * 55)
    print("  裁判書開放資料解壓縮工具")
    print(f"  來源：{SOURCE_DIR}")
    print(f"  目標：{DEST_DIR}")
    print("=" * 55)

    all_rars = get_rar_list()
    years = sorted({r.stem[:4] for r in all_rars if r.stem[:4].isdigit()})
    print(f"共找到 {len(all_rars)} 個 RAR 檔，年份範圍：{years[0]}～{years[-1]}\n")

    print("請選擇解壓縮範圍：")
    print("  1. 僅解壓縮近3年（2023-2025，供112-114年研究用）")
    print("  2. 自訂西元年份範圍")
    print("  3. 全部解壓縮（約需大量磁碟空間）")
    print("  0. 取消")

    choice = input("\n請輸入選項 [1/2/3/0]: ").strip()

    if choice == "1":
        rars = get_rar_list(2023, 2025)
        print(f"\n找到 {len(rars)} 個符合條件的 RAR 檔。")
        confirm = input("確認開始解壓縮？[Y/n]: ").strip().lower()
        if confirm in ("", "y"):
            run_extraction(rars)

    elif choice == "2":
        try:
            y1 = int(input("  起始年份（西元，如 2023）：").strip())
            y2 = int(input("  結束年份（西元，如 2025）：").strip())
            rars = get_rar_list(y1, y2)
            print(f"\n找到 {len(rars)} 個符合條件的 RAR 檔。")
            confirm = input("確認開始解壓縮？[Y/n]: ").strip().lower()
            if confirm in ("", "y"):
                run_extraction(rars)
        except ValueError:
            print("[ERROR] 年份格式錯誤")

    elif choice == "3":
        total_size = sum(r.stat().st_size for r in all_rars)
        print(f"\n⚠  全部解壓縮共 {len(all_rars)} 個，壓縮後總大小 {human_size(total_size)}，解壓後約為 5-10 倍。")
        confirm = input("確認開始？[Y/n]: ").strip().lower()
        if confirm in ("", "y"):
            run_extraction(all_rars)

    else:
        print("已取消。")


def main():
    parser = argparse.ArgumentParser(description="裁判書開放資料 RAR 解壓縮工具")
    parser.add_argument("--all", action="store_true", help="解壓縮全部")
    parser.add_argument("--years", metavar="YYYY-YYYY", help="西元年份範圍，如 2023-2025")
    args = parser.parse_args()

    if not check_env():
        sys.exit(1)

    if args.all:
        rars = get_rar_list()
        run_extraction(rars)
    elif args.years:
        try:
            y1, y2 = [int(y) for y in args.years.split("-")]
            rars = get_rar_list(y1, y2)
            run_extraction(rars)
        except Exception:
            print("[ERROR] --years 格式應為 YYYY-YYYY，如 2023-2025")
            sys.exit(1)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
