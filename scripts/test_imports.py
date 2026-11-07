import sys

print("Testing scipy...")
try:
    import scipy
    print("scipy version:", scipy.__version__)
except Exception as e:
    print("scipy error:", e)

print("Testing sklearn...")
try:
    import sklearn
    print("sklearn version:", sklearn.__version__)
except Exception as e:
    print("sklearn error:", e)

print("Testing pandas...")
try:
    import pandas
    print("pandas version:", pandas.__version__)
except Exception as e:
    print("pandas error:", e)
