import os
import plotly.graph_objects as graph


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
    directory = f"MEM/{path}"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/{filename}.MEM", "w") as file:
        file.write("Scanpts: 1, 40, 411, 450\r\n")      # indicates the pre-scan and post-scan limits, these work for our scan of 450
        i = 0
        for stimulus, response in zip(stimuli, responses):
            i += 1
            file.write(f"MS.{i:<8}{stimulus:<30} {response}\r\n")


def generateMEF(path, filenames):
    directory = f"MEM/{path}"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/batch.MEF", "w") as file:
        for filename in filenames:
            file.write(f"{filename}\r\n")


def generateTXT(path, filename, data):
    directory = f"RAW/{path}"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/{filename}.txt", "w") as file:
        for item in data:      
            file.write(f"{item}\n")


def generatePlot(path, filename, stimuli, responses):
    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=stimuli, y=responses, mode="markers"))

    directory = f"PLOTS/{path}"
    os.makedirs(directory, exist_ok=True)
    fig.write_image(f"{directory}/{filename}.png")      # save the plot to the specified path


def generateTrajectory(path, filename, mu_counts, max_CMAPs):
    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=mu_counts, y=max_CMAPs, mode="markers"))

    directory = f"TRAJECTORIES/{path}"
    os.makedirs(directory, exist_ok=True)
    fig.write_image(f"{directory}/{filename}.png")      # save the plot to the specified path