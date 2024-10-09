import os
import plotly.graph_objects as graph

PATH = "de-random/re-distributed/str-0.2"

for filename in os.listdir(f"MEM/{PATH}"):
    if filename.endswith("MEM"):                                    # find MScanFit output file
        [mu_count, mu_mean] = filename.strip(".MEM").split('-')     # gather some filename variables for later

        start = None            # will store index after which the relevant data is stored in the file
        mune = None             # will store the MScanFit MUNE
        mune_sizes = []         # will store the MScanFit MUSEs (Motor Unit Size Estimates)
        mune_scale = None       # will store the scale factor for MUSEs, since outputs are given as a % of peak amplitude
        mu_sizes = []           # will store the actual MU sizes

        with open(f"MEM/{PATH}/{filename}", 'r') as file:
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

        with open(f"RAW/{PATH}/mu-{mu_count}/{mu_mean}.txt") as file:
            for line in file:
                mu_sizes.append(round(float(line), 4))      # get the actual MU sizes from the RAW data

        directory = f"ANALYSIS/{PATH}/mu-{mu_count}"
        os.makedirs(directory, exist_ok=True)

        fig = graph.Figure()
        fig.update_layout(title=f"MUNE={mune} | RAW={mu_count}", xaxis_title="Motor Unit",  yaxis_title="Amplitude (mV)")
        fig.add_trace(graph.Scatter(x=list(range(1,len(mune_sizes))), y=sorted(mune_sizes), mode="markers", name="MUNE"))
        fig.add_trace(graph.Scatter(x=list(range(1,len(mu_sizes))),y=sorted(mu_sizes), mode="markers", name = "RAW"))
        fig.write_image(f"{directory}/{mu_mean}.png")