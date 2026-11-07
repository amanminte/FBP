import sys

print("Checking sys...", flush=True)
import os
print("Checking os...", flush=True)

print("Checking numpy...", flush=True)
import numpy as np
print(f"NumPy OK: {np.__version__}", flush=True)

print("Checking pandas...", flush=True)
import pandas as pd
print(f"Pandas OK: {pd.__version__}", flush=True)

print("Checking joblib...", flush=True)
import joblib
print(f"Joblib OK: {joblib.__version__}", flush=True)

print("Checking yaml...", flush=True)
import yaml
print(f"YAML OK: {yaml.__version__}", flush=True)

print("Checking matplotlib...", flush=True)
import matplotlib
print(f"Matplotlib OK: {matplotlib.__version__}", flush=True)

print("Checking scipy...", flush=True)
import scipy
print(f"Scipy OK: {scipy.__version__}", flush=True)

print("Checking sklearn...", flush=True)
import sklearn
print(f"Sklearn OK: {sklearn.__version__}", flush=True)

print("All imports tested!", flush=True)
