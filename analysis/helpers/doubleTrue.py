import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import sys
from collections import Counter

df_list = []
files = ['rateTest.csv']

for f in files: 
    # Read & add files as dataframes 
    df = pd.read_csv(f)
    df_list.append(df)

for df in df_list:
    good = df['goodTrk']
    evtTrackCounter = Counter(df[good]['evtNum'])
    print(str(df[good]['evtNum']))
    for x in evtTrackCounter:
        # print(f"evtTrackCounter[{x}]: {evtTrackCounter[x]}")
        if evtTrackCounter[x] > 1:
            print(f"evt {x} has multiple good tracks")

