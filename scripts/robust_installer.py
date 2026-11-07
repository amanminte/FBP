"""
Robust Package Installer with Network Fluctuation Self-Healing
Handles temporary network drops (3-5 mins) by retrying continuously until installed.
"""
import subprocess
import sys
import time
import importlib.util

PACKAGES = [
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("pandas", "pandas"),
    ("scikit-learn", "sklearn"),
    ("pyyaml", "yaml"),
    ("joblib", "joblib"),
    ("requests", "requests"),
    ("matplotlib", "matplotlib"),
    ("seaborn", "seaborn"),
    ("optuna", "optuna"),
    ("lightgbm", "lightgbm"),
    ("xgboost", "xgboost"),
    ("catboost", "catboost"),
    ("streamlit", "streamlit"),
]

def is_installed(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False

def install_package(pkg_name: str, module_name: str, max_retries: int = 50):
    if is_installed(module_name):
        print(f"[OK] {pkg_name} ({module_name}) is already installed.")
        return True

    print(f"[INSTALLING] {pkg_name}...")
    attempt = 1
    while attempt <= max_retries:
        try:
            print(f"--> Attempt {attempt}/{max_retries} for {pkg_name}...")
            cmd = [
                sys.executable, "-m", "pip", "install", pkg_name,
                "--timeout", "60",
                "--retries", "10"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[SUCCESS] {pkg_name} successfully installed!")
                return True
            else:
                err_msg = result.stderr.strip() or result.stdout.strip()
                print(f"[RETRY] Failed to install {pkg_name}. Error snippet: {err_msg[-200:]}")
                print(f"Waiting 15 seconds before retry (network drop resilience)...")
                time.sleep(15)
                attempt += 1
        except Exception as e:
            print(f"[EXCEPTION] {e}. Waiting 15 seconds...")
            time.sleep(15)
            attempt += 1

    raise RuntimeError(f"Could not install {pkg_name} after {max_retries} attempts.")

def main():
    print("=" * 60)
    print("STARTING ROBUST INSTALLATION LOOP")
    print("=" * 60)
    for pkg_name, module_name in PACKAGES:
        install_package(pkg_name, module_name)
    print("=" * 60)
    print("ALL DEPENDENCIES VERIFIED AND READY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
