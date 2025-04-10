import os
import pandas as pd
import matplotlib.pyplot as plt
import dabest

DIR_IN = "ANALYSIS/MEM-RS2.0"
paths = ["de-random/re-random/str-0.6"]

def test(paths):
    for path in paths:
        df = pd.read_csv(f"{DIR_IN}/{path}/MUNE (abs % err).csv", index_col=0)
        df = df.melt(var_name="group", value_name="value")
        output = dabest.load(data=df, x="group", y="value", idx=("MU5", "MU10", "MU20", "MU40", "MU80", "MU160")).mean_diff
        print(output.results.filter(["bca_low", "bca_high"]))
        fig = output.plot(raw_marker_size=3, es_marker_size=3)
        plt.show()

test(paths)