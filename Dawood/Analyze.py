import os
import numpy as np
import pandas as pd
import plotly.graph_objects as graph
import matplotlib.pyplot as plt
import dabest

DE_CONDITIONS = [
                    "random",
                    "selective"
                ]
RE_CONDITIONS = [
                    "random",
                    "selective",
                    "distributive",
                    "none"
                ] # none must be last
STR_CONDITIONS = [
                    "0.2",
                    "0.6"
                ]

DIR_IN = "MEM-RS2.0"                      #### EDIT THIS DEPENDING ON DATASET PROPERTIES
DIR_OUT = "ANALYSIS/MEM-RS2.0"     #### EDIT THIS DEPENDING ON DATASET PROPERTIES

PATHS = []

def main():
    for de_condition in DE_CONDITIONS:
        for re_condition in RE_CONDITIONS:
            if re_condition == "none":
                    PATHS.append(f"de-{de_condition}/re-{re_condition}/str-0.2")
                    break
            for str_condition in STR_CONDITIONS:
                PATHS.append(f"de-{de_condition}/re-{re_condition}/str-{str_condition}")

    measures = ["MUNE",
                "MUNE (% err)",
                "MUNE (abs % err)",
                "LSU target (µV)",
                "LSUE (µV)",
                "LSUE (abs err, µV)",
                "MSU target (µV)",
                "MSUE (µV)",
                "MSUE (abs err, µV)"]
    aggregate = {measure: {} for measure in measures}

    for path in PATHS:
        data = {}
        for filename in os.listdir(f"{DIR_IN}/{path}"):
            if filename.endswith("MEM"):                                            # find MScanFit output file
                [mu_count, iteration] = filename.strip(".MEM").split('-')           # gather some filename variables for later
                mu_count = int(mu_count)
                data.setdefault(mu_count, {measure: [] for measure in measures})    # initialize a column to store data for this MU count

                start = None            # will store index after which the relevant data is stored in the file
                mune = None             # will store the MScanFit MUNE
                mune_thresholds = []
                mune_sizes = []         # will store the MScanFit MUSEs (Motor Unit Size Estimates)
                mune_scale = None       # will store the scale factor for MUSEs, since outputs are given as a % of peak amplitude
                mu_thresholds = []
                mu_sizes = []           # will store the actual MU sizes

                with open(f"{DIR_IN}/{path}/{filename}", 'r') as file:
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
                                mune_thresholds.append(round(float(values[2]), 4))
                                mune_sizes.append(round(float(values[3]) * mune_scale, 4))      # get the MUSEs

                with open(f"RAW/{path}/mu-{mu_count}/{iteration}.txt", 'r') as file:
                    for line in file:
                        mu_thresholds.append(round(float(line.split('\t')[0]), 4))
                        mu_sizes.append(round(float(line.split('\t')[1]), 4))      # get the actual MU sizes from the RAW data (ground truth)

                # try:
                #     data[mu_count]["MUNE"].append(mune)
                #     data[mu_count]["MUNE (% err)"].append((mune - mu_count) / mu_count * 100)
                #     data[mu_count]["MUNE (abs % err)"].append(abs(mune - mu_count) / mu_count * 100)
                #     data[mu_count]["LSU target (µV)"].append(np.max(mu_sizes) * 1000)
                #     data[mu_count]["LSUE (µV)"].append(np.max(mune_sizes) * 1000)
                #     data[mu_count]["LSUE (abs err, µV)"].append(abs(np.max(mune_sizes) - np.max(mu_sizes)) * 1000)
                #     data[mu_count]["MSU target (µV)"].append(np.mean(mu_sizes) * 1000)
                #     data[mu_count]["MSUE (µV)"].append(np.mean(mune_sizes) * 1000)
                #     data[mu_count]["MSUE (abs err, µV)"].append(abs(np.mean(mune_sizes) - np.mean(mu_sizes)) * 1000)
                    
                #     for measure in aggregate:
                #         aggregate[measure].setdefault(path, [])     # initialize a column to store data for this condition
                #     aggregate["MUNE"][path].append({mu_count: mune})
                #     aggregate["MUNE (% err)"][path].append({mu_count: (mune - mu_count) / mu_count * 100})
                #     aggregate["MUNE (abs % err)"][path].append({mu_count: abs(mune - mu_count) / mu_count * 100})
                #     aggregate["LSU target (µV)"][path].append({mu_count: np.max(mu_sizes) * 1000})
                #     aggregate["LSUE (µV)"][path].append({mu_count: np.max(mune_sizes) * 1000})
                #     aggregate["LSUE (abs err, µV)"][path].append({mu_count: abs(np.max(mune_sizes) - np.max(mu_sizes)) * 1000})
                #     aggregate["MSU target (µV)"][path].append({mu_count: np.mean(mu_sizes) * 1000})
                #     aggregate["MSUE (µV)"][path].append({mu_count: np.mean(mune_sizes) * 1000})
                #     aggregate["MSUE (abs err, µV)"][path].append({mu_count: abs(np.mean(mune_sizes) - np.mean(mu_sizes)) * 1000})
                # except:
                #     print(f"missing values: {path}/{mu_count}-{iteration}")

                # # Plot stuff
                directory = f"{DIR_OUT}/{path}/mu-{mu_count}"
                os.makedirs(directory, exist_ok=True)
                # fig = graph.Figure()
                # fig.update_layout(title=f"MUNE={mune}-{sum(mune_sizes)} | RAW={mu_count}-{sum(mu_sizes)}", xaxis_title="Motor Unit",  yaxis_title="Amplitude (mV)")
                # fig.add_trace(graph.Scatter(x=list(range(1,len(mune_sizes)+1)), y=sorted(mune_sizes), mode="markers", name="MUNE"))
                # fig.add_trace(graph.Scatter(x=list(range(1,len(mu_sizes)+1)),y=sorted(mu_sizes), mode="markers", name = "RAW"))
                # fig.write_image(f"{directory}/{iteration}.png")

                hungarian(directory, iteration, mune, mu_count, mune_thresholds, mune_sizes, mu_thresholds, mu_sizes)

    #     try:
    #         df = pd.DataFrame(data)                                                 # convert the data dictionary to a readable dataframe
    #         for col in df.columns:
    #             for i, row in enumerate(df[col]):
    #                 df[col].iloc[i] = f"{np.mean(row):.2f} ± {np.std(row):.2f}"     # collapse iteration dimension into mean ± SD
    #         df = df.reindex(sorted(df.columns, key=int), axis=1)                    # sort the column heading MU counts
    #         df["Combined"] = df.apply(lambda row: f"{np.mean([float(x.split(' ± ')[0]) for x in row]):.2f} ± {np.std([float(x.split(' ± ')[0]) for x in row]):.2f}", axis=1)
    #         df.to_csv(f"{DIR_OUT}/{path}/summary.csv", index=True)
    #     except:
    #         print(f"summary not created: {path}")

    # for measure in measures:
    #     aggregate[measure]["de-random/re-selective/str-0.2"].append({5: None})
    #     aggregate[measure]["de-random/re-none/str-0.2"].append({5: None})
    #     for key in aggregate[measure]:
    #         aggregate[measure][key] = sorted(aggregate[measure][key], key=lambda x: list(x.keys())[0])
    #     df = pd.DataFrame.from_dict(aggregate[measure], orient="index").transpose()
    #     df = df.apply(lambda col: col.apply(lambda x: list(x.values())[0]))
    #     short_cols = [f"{''.join([word.split('-')[1][0] for word in col.split('/')[0:2]])}{col[-1]}0" for col in df.columns]
    #     df.to_csv(f"{DIR_OUT}/{measure}.csv", header=short_cols)

    #     df_temp = df.__deepcopy__()
    #     df_temp.columns = short_cols
    #     df_temp = df_temp.melt(var_name="group", value_name="value")
    #     test = dabest.load(data=df_temp, x="group", y="value", idx=tuple(short_cols))
    #     fig = test.mean_diff.plot(raw_marker_size=3)
    #     plt.savefig(f"{DIR_OUT}/{measure}.png")

    #     for col in df.columns:
    #         temp = [[] for _ in range(6)]
    #         for i in range(len(df[col])):
    #             temp[i // 10].append(df[col].iloc[i])
    #         df_temp = pd.DataFrame(temp, [5, 10, 20, 40, 80, 160]).transpose()
    #         df_temp.columns = [f"MU{col}" for col in df_temp.columns]
    #         df_temp.to_csv(f"{DIR_OUT}/{col}/{measure}.csv")

    #         df_temp = df_temp.melt(var_name="group", value_name="value")
    #         test = dabest.load(data=df_temp, x="group", y="value", idx=("MU5", "MU10", "MU20", "MU40", "MU80", "MU160"))
    #         fig = test.mean_diff.plot(raw_marker_size=3)
    #         plt.savefig(f"{DIR_OUT}/{col}/{measure}.png")

def hungarian(directory, iteration, mune, mu_count, mune_thresholds, mune_sizes, mu_thresholds, mu_sizes):

    with open(f"{directory}/{iteration}.txt", 'w') as file:
        file.write(f"MUNE size mean: {np.mean(mune_sizes)}\n")
        file.write(f"MU size mean: {np.mean(mu_sizes)}\n")

    # Plot stuff
    fig = graph.Figure()
    fig.update_layout(title=f"MUNE={mune}-{sum(mune_sizes)} | GROUND TRUTH={mu_count}-{sum(mu_sizes)}", xaxis_title="Threshold Mean (mA)",  yaxis_title="Amplitude (mV)")
    fig.add_trace(graph.Scatter(x=mune_thresholds, y=mune_sizes, mode="markers", name="MUNE"))
    fig.add_trace(graph.Scatter(x=mu_thresholds,y=mu_sizes, mode="markers", name = "GROUND TRUTH"))
    fig.write_image(f"{directory}/{iteration}-unsorted.png")

main()