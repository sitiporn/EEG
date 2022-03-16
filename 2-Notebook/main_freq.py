import os 
from config import *

for i in range(len(fmax_range)):
    os.system(f'python3 02_ArtifactRemoval_Epoching_psd-freq.py freq {files[0]} {fmin_range[i]} {fmax_range[i]}')
    os.system(f'python3 03_FeatureExtraction-CNN-freq.py freq {files[0]} {task} {fmin_range[i]} {fmax_range[i]}')
