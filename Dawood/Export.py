import os
import plotly.graph_objects as graph
import plotly.express as px
import matplotlib.pyplot as plt

MEM_PATH = "MEM-Oct10"

def generateDAT(path, filename, stimuli, responses):
    """ Export stimulus-response data from simulation to MScanFit-compatible .DAT file
            path - directory to save file in
            filename - name to save file as
            stimuli - x-axis stimulus (mA) data
            responses - y-axis resposne (mV) data
    """
    
    directory = f"DAT/{path}"                   # set an appropriate path for the data
    os.makedirs(directory, exist_ok=True)       # ensure all intermediate directories are created

    with open(f"{directory}/{filename}.DAT", "w") as file:
        for stimulus, response in zip(stimuli, responses):      # zip() function pairs elements from both arrays into tuples
            file.write(f"{stimulus:<30} {response}\r\n")        # \r\n is the MScanFit-compatible (Windows) newline character


def generateMEM(path, filename, stimuli, responses):
    directory = f"{MEM_PATH}/{path}"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/{filename}.MEM", "w") as file:
        file.write("Scanpts: 1, 20, 481, 500\r\n")      # indicates the pre-scan and post-scan limits, these work for our scan of 450
        i = 0
        for stimulus, response in zip(stimuli, responses):
            i += 1
            file.write(f"MS.{i:<8}{stimulus:<30} {response}\r\n")


def generateMEF(path, filenames):
    directory = f"{MEM_PATH}/{path}"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/batch.MEF", "w") as file:
        for filename in filenames:
            file.write(f"{filename}\r\n")


def generateTXT(path, filename, thresholds, sizes):
    directory = f"RAW/{path}"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/{filename}.txt", "w") as file:
        for i in range(len(thresholds)):      
            file.write(f"{thresholds[i]}\t{sizes[i]}\n")


def generatePlot(path, filename, stimuli, responses):
    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=stimuli, y=responses, mode="markers", marker=dict(color="black", size=4)))
    fig.update_layout(
        template="plotly_white",          # Base template for minimal styling
        plot_bgcolor="rgba(0,0,0,0)",     # Transparent plot background
        xaxis=dict(
            title="Stimulus Intensity (mA)",
            color="black",                # Black x-axis line and labels
            showgrid=False,               # Show only main gridline for x-axis
            zeroline=True,                # Show main gridline at zero
            zerolinecolor="black"         # Make zero line black
        ),
        yaxis=dict(
            title="CMAP Amplitude (mV)",
            color="black",                # Black y-axis line and labels
            showgrid=False,               # Show only main gridline for y-axis
            zeroline=True,                # Show main gridline at zero
            zerolinecolor="black"         # Make zero line black
        )
    )

    directory = f"PLOTS/{path}"
    os.makedirs(directory, exist_ok=True)
    fig.write_image(f"{directory}/{filename}.png")      # save the plot to the specified path


def generateTrajectory(path, filename, mu_counts, max_CMAPs):
    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=mu_counts,
                                y=max_CMAPs,
                                mode="lines+markers+text",
                                text=[f"{y:.2f}" for y in max_CMAPs],
                                textposition="top center"))
    fig.update_layout(yaxis_range=[0, 12])

    directory = f"TRAJECTORIES/{path}"
    os.makedirs(directory, exist_ok=True)
    fig.write_image(f"{directory}/{filename}.png")


def generateDist(path, filename, data):
    fig = px.histogram(x=data, nbins=15)
    # fig.update_traces(xbins=dict(
    #     start=0,  # Start of the bins
    #     end=0.5,   # End of the bins
    #     size=0.02  # Size of each bin
    # ))
    # fig.update_layout(xaxis=dict(range=[0, 0.6]))

    directory = f"DISTS/{path}"
    os.makedirs(directory, exist_ok=True)
    fig.write_image(f"{directory}/{filename}.png")

def showDist(data):
    fig = px.histogram(x=data, nbins=15)
    # fig.update_traces(xbins=dict(
    #     start=0,  # Start of the bins
    #     end=0.5,   # End of the bins
    #     size=0.02  # Size of each bin
    # ))
    # fig.update_layout(xaxis=dict(range=[0, 0.6]))

    fig.show()

def showPlot(x, y):
    plt.figure()
    plt.plot(y, marker='o', linestyle='none')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()