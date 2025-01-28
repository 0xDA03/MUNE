import os
import numpy as np
import pandas as pd
import plotly.graph_objects as graph

DE_CONDITIONS = [
                    "random",
                    #"selective"
                ]
RE_CONDITIONS = [
                    "random",
                    #"selective",
                    #"distributive",
                    #"none"
                ] # none must be last
STR_CONDITIONS = [
                    #"0.2",
                    "0.6"
                ]
PATHS = []
for de_condition in DE_CONDITIONS:
    for re_condition in RE_CONDITIONS:
        if re_condition == "none":
                PATHS.append(f"de-{de_condition}/re-{re_condition}/str-0.2")
                break
        for str_condition in STR_CONDITIONS:
            PATHS.append(f"de-{de_condition}/re-{re_condition}/str-{str_condition}")

data = {}

for path in PATHS:
    for filename in os.listdir(f"MEM/{path}"):
        if filename.endswith("MEM"):                                        # find MScanFit output file
            [mu_count, iteration] = filename.strip(".MEM").split('-')       # gather some filename variables for later
            data.setdefault(mu_count, {"MUNE":[],
                                       "MUNE (% err)":[],
                                       "MUNE (abs % err)":[],
                                       "LSU target (µV)": [],
                                       "LSUE (µV)": [],
                                       "LSUE (abs err, µV)": [],
                                       "MSU target (µV)": [],
                                       "MSUE (µV)": [],
                                       "MSUE (abs err, µV)": []})           # initialize a column to store data for this MU count

            start = None            # will store index after which the relevant data is stored in the file
            mune = None             # will store the MScanFit MUNE
            mune_sizes = []         # will store the MScanFit MUSEs (Motor Unit Size Estimates)
            mune_scale = None       # will store the scale factor for MUSEs, since outputs are given as a % of peak amplitude
            mu_sizes = []           # will store the actual MU sizes

            with open(f"MEM/{path}/{filename}", 'r') as file:
                for index, line in enumerate(file):
                    if line.startswith("MSFPeakAmp(mV)"):
                        mune_scale = float(line.split('=')[1]) / 100                        # get the MUSE scale factor
                    if line.startswith("!MScan Model"):
                        start = index                                                       # get the start index
                    if start:
                        if index == start + 1:
                            mune = int(line[1:])                                            # get the MUNE
                        elif index > start and index <= start + mune + 1:
                            values = line.split('\t')
                            mune_sizes.append(round(float(values[3]) * mune_scale, 4))      # get the MUSEs

            with open(f"RAW/{path}/mu-{mu_count}/{iteration}.txt") as file:
                for line in file:
                    mu_sizes.append(round(float(line), 4))      # get the actual MU sizes from the RAW data (ground truth)

            data[mu_count]["MUNE"].append(mune)
            data[mu_count]["MUNE (% err)"].append((mune - int(mu_count)) / int(mu_count) * 100)
            data[mu_count]["MUNE (abs % err)"].append(abs(mune - int(mu_count)) / int(mu_count) * 100)
            data[mu_count]["LSU target (µV)"].append(np.max(mu_sizes) * 1000)
            data[mu_count]["LSUE (µV)"].append(np.max(mune_sizes) * 1000)
            data[mu_count]["LSUE (abs err, µV)"].append(abs(np.max(mune_sizes) - np.max(mu_sizes)) * 1000)
            data[mu_count]["MSU target (µV)"].append(np.mean(mu_sizes) * 1000)
            data[mu_count]["MSUE (µV)"].append(np.mean(mune_sizes) * 1000)
            data[mu_count]["MSUE (abs err, µV)"].append(abs(np.mean(mune_sizes) - np.mean(mu_sizes)) * 1000)

            # Plot stuff
            directory = f"ANALYSIS/{path}/mu-{mu_count}"
            os.makedirs(directory, exist_ok=True)
            fig = graph.Figure()
            fig.update_layout(title=f"MUNE={mune}-{sum(mune_sizes)} | RAW={mu_count}-{sum(mu_sizes)}", xaxis_title="Motor Unit",  yaxis_title="Amplitude (mV)")
            fig.add_trace(graph.Scatter(x=list(range(1,len(mune_sizes)+1)), y=sorted(mune_sizes), mode="markers", name="MUNE"))
            fig.add_trace(graph.Scatter(x=list(range(1,len(mu_sizes)+1)),y=sorted(mu_sizes), mode="markers", name = "RAW"))
            fig.write_image(f"{directory}/{iteration}.png")

    df = pd.DataFrame(data)                                                 # convert the data dictionary to a readable dataframe
    for col in df.columns:
        for i, row in enumerate(df[col]):
            df[col].iloc[i] = f"{np.mean(row):.2f} ± {np.std(row):.2f}"     # collapse iteration dimension into mean ± SD
    df = df.reindex(sorted(df.columns, key=int), axis=1)                    # sort the column heading MU counts
    df["Combined"] = df.apply(lambda row: f"{np.mean([float(x.split(' ± ')[0]) for x in row]):.2f} ± {np.std([float(x.split(' ± ')[0]) for x in row]):.2f}", axis=1)

    df.to_csv(f"ANALYSIS/{path}/summary.csv", index=True)