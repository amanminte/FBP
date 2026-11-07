"""
Multi-season Data Downloader with Network-Drop Resilience & Caching.
Downloads 6 seasons (19/20 to 24/25) for top 5 European leagues from Football-Data.co.uk.
"""
import os
import time
import requests
import pandas as pd
from typing import Dict, List, Optional

LEAGUES = {
    "E0": "English Premier League",
    "SP1": "Spanish La Liga",
    "I1": "Italian Serie A",
    "D1": "German Bundesliga",
    "F1": "French Ligue 1"
}

SEASONS = ["1718", "1819", "1920", "2021", "2122", "2223", "2324", "2425"]
BASE_URL = "https://www.football-data.co.uk/mmz4281"

def download_file_with_retry(url: str, dest_path: str, max_retries: int = 10, backoff: int = 5) -> bool:
    """Downloads a file with automatic retries for network resilience."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        print(f"[CACHE HIT] {os.path.basename(dest_path)} exists ({os.path.getsize(dest_path)} bytes).")
        return True

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    temp_path = dest_path + ".tmp"

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[DOWNLOAD] Attempt {attempt}/{max_retries} for {url}...")
            response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200 and len(response.content) > 500:
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                os.rename(temp_path, dest_path)
                print(f"[SUCCESS] Saved {dest_path} ({len(response.content)} bytes).")
                return True
            else:
                print(f"[WARN] Status {response.status_code} or small payload ({len(response.content)} bytes).")
        except Exception as e:
            print(f"[NETWORK ERROR] {e}. Waiting {backoff * attempt}s before retry...")
        time.sleep(backoff * attempt)

    if os.path.exists(temp_path):
        os.remove(temp_path)
    return False

def download_all_historical_data(raw_dir: str = "data/raw", force: bool = False) -> Dict[str, str]:
    """Downloads all season/league CSVs and returns mapping of key to file path."""
    os.makedirs(raw_dir, exist_ok=True)
    downloaded_files = {}

    for season in SEASONS:
        for league in LEAGUES.keys():
            key = f"{season}_{league}"
            url = f"{BASE_URL}/{season}/{league}.csv"
            dest = os.path.join(raw_dir, f"{key}.csv")
            if force and os.path.exists(dest):
                os.remove(dest)
            success = download_file_with_retry(url, dest)
            if success:
                downloaded_files[key] = dest
            else:
                print(f"[ERROR] Could not download {url} after retries.")

    return downloaded_files

def load_raw_dataset(raw_dir: str = "data/raw") -> pd.DataFrame:
    """Reads all raw CSVs into a single combined pandas DataFrame with league and season columns."""
    dfs = []
    for season in SEASONS:
        for league in LEAGUES.keys():
            file_path = os.path.join(raw_dir, f"{season}_{league}.csv")
            if not os.path.exists(file_path):
                continue
            try:
                # football-data.co.uk csv files can have latin1 encoding
                df = pd.read_csv(file_path, encoding="latin1", on_bad_lines="skip")
                df["League"] = league
                df["Season"] = season
                dfs.append(df)
            except Exception as e:
                print(f"[WARN] Error reading {file_path}: {e}")

    if not dfs:
        raise FileNotFoundError(f"No valid CSVs found in {raw_dir}")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"[DATA LOADED] Total raw matches: {len(combined)}")
    return combined

if __name__ == "__main__":
    download_all_historical_data()
    df = load_raw_dataset()
    print(f"Summary by League:\n{df['League'].value_counts()}")
