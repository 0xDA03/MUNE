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


def generateTXT(path, filename, data):
    directory = f"RAW/{path}"                   # set an appropriate path for the plot
    os.makedirs(directory, exist_ok=True)       # ensure all intermediate directories are created

    with open(f"{directory}/{filename}.txt", "w") as file:
        for item in data:      
            file.write(f"{item}\n")


def generatePlot(path, filename, stimuli, responses):
    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=stimuli, y=responses, mode="markers"))

    directory = f"PLOTS/{path}"                         # set an appropriate path for the plot
    os.makedirs(directory, exist_ok=True)               # ensure all intermediate directories are created
    fig.write_image(f"{directory}/{filename}.png")      # save the plot to the specified path