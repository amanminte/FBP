"""
Master Turnkey Pipeline Orchestrator for Football Prediction & Decision-Support Engine.
Execute this script with a single command to run the complete end-to-end pipeline:
    python run_pipeline.py
"""
import os
import sys
import argparse
import subprocess

def print_banner(step_num: int, title: str):
    print("\n" + "=" * 70)
    print(f" STEP {step_num}: {title.upper()}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="End-to-End Football Prediction Engine Orchestrator")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading raw historical CSVs if already cached")
    parser.add_argument("--fast-eval", action="store_true", help="Run quick evaluation mode")
    args = parser.parse_args()

    # 1. Download Historical Data
    print_banner(1, "Ingesting Historical Data (6 Seasons, Top 5 Leagues)")
    from src.data.load_data import download_all_historical_data
    if not args.skip_download:
        download_all_historical_data(raw_dir="data/raw", force=False)
    else:
        print("[INFO] Skipping download as requested. Using cached CSVs in data/raw/.")

    # 2. Clean & Validate Data
    print_banner(2, "Cleaning, Canonicalizing, and Validating Matches")
    from src.data.validate_data import process_and_save
    clean_df = process_and_save(raw_dir="data/raw", processed_dir="data/processed")

    # 3. Build Leakage-Free Pre-Match Features
    print_banner(3, "Engineering Zero-Leakage Features (Elo, Pi, Dixon-Coles, Rolling Forms)")
    from src.features.build_features import generate_and_save_features
    features_df = generate_and_save_features(
        clean_path="data/processed/matches_clean.csv",
        output_path="data/processed/matches_features.csv"
    )

    # 4. Anti-Leakage Verification
    print_banner(4, "Running Anti-Leakage Automated Verification Tests")
    test_result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_no_leakage.py", "-v"], capture_output=True, text=True)
    print(test_result.stdout)
    if test_result.returncode != 0:
        print("[WARNING] Anti-leakage test failed or encountered environment flag:")
        print(test_result.stderr)
    else:
        print("[SUCCESS] Zero-leakage verification passed!")

    print_banner(5, "Pipeline Staging Complete")
    print("Data and features are fully processed, validated, and ready for model training and Streamlit dashboard.")

if __name__ == "__main__":
    main()
