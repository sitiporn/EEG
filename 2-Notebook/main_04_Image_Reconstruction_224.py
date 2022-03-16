import os 
from config import *

for f in files:
    i = int(f.split("-")[0])
    os.system(f'python3 04_Image_Reconstruction_224.py par{i} {f} {task}')


