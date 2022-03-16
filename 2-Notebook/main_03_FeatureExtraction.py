import os 
from config import *

for f in files:
    i = int(f.split("-")[0])
    os.system(f'python3 03_FeatureExtraction-CNN.py par{i} {f} {task}')
