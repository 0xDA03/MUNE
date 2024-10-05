import tkinter as tk
from tkinter import ttk  # Importing ttk for Combobox
import numpy as np
from scipy.stats import expon
from scipy.special import erf
import plotly.graph_objects as graph
from io import BytesIO
from PIL import Image, ImageTk

# Global dictionary to store all plot images by re_strength
plot_images_dict = {}
current_image_idx = 0
current_re_strength = None

def main():
    global mu_count_0, mu_count, resiliences, rng
    THRESHOLD_MIN = 0.025
    seed = np.random.randint(1000000)

    for re_strength in resiliences:
        re_strength /= 100
        rng = np.random.default_rng(seed=seed)
        mu_sizes = expon.rvs(scale=smup_mean - THRESHOLD_MIN, loc=THRESHOLD_MIN, size=mu_count_0, random_state=rng)
        plot_images_dict[re_strength] = []  # Initialize list for each re_strength
        mu_sizes = np.sort(mu_sizes)
        while len(mu_sizes) >= 5:
            mu_count = len(mu_sizes)

            stimuli, responses = scan(mu_sizes)
            store_plot(stimuli, responses, re_strength)  # Store each plot for the current re_strength

            mu_sizes = degenerate(mu_sizes, mu_count, re_strength)  # Handle degeneration

def scan(mu_sizes):
    global mu_count, smup_mean, threshold_mean, threshold_dev, rng

    THRESHOLD_SPREAD = 0.0165
    SAMPLES = 450
    NOISE = 0.01

    mu_count = len(mu_sizes)
    mu_thresholds = rng.normal(threshold_mean, threshold_dev, mu_count)
    mu_devs = mu_thresholds * THRESHOLD_SPREAD
    stimuli = np.linspace(min(mu_thresholds) - 0.5, max(mu_thresholds) + 0.5, SAMPLES)
    noise = rng.normal(0, NOISE, SAMPLES)

    responses = []
    for stimulus in stimuli:
        probabilities = (erf((1 / (np.sqrt(2) * mu_devs)) * (stimulus - mu_thresholds)) + 1) / 2
        activations = rng.uniform(0, 1, mu_count) <= probabilities
        cmap = np.sum(mu_sizes * (activations.astype(int)))
        responses.append(cmap)
    responses = np.array(responses) + noise

    return stimuli, responses

def degenerate(mu_sizes, mu_count, re_strength):
    mu_sizes = np.sort(mu_sizes)
    de_sizes = mu_sizes[int(mu_count * 0.5):]
    mu_sizes = np.setdiff1d(mu_sizes, de_sizes, assume_unique=True)

    de_sum = np.sum(de_sizes)
    re_amplitude = de_sum * re_strength / len(mu_sizes)
    for i in range(len(mu_sizes)):
        mu_sizes[i] += re_amplitude

    return mu_sizes

def create_plot(stimuli, responses, re_strength):
    global mu_count
    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=stimuli, y=responses, mode='markers'))
    fig.update_layout(title=f"CMAP Scan | {mu_count} Motor Units | {re_strength * 100}% Resilience", 
                      xaxis_title='Stimulus Intensity (mA)', 
                      yaxis_title='Amplitude (mV)')

    img_data = fig.to_image(format="png")
    return img_data

# Function to store the Plotly image in the plot_images_dict
def store_plot(stimuli, responses, re_strength):
    img_data = create_plot(stimuli, responses, re_strength)

    img = Image.open(BytesIO(img_data))
    img_tk = ImageTk.PhotoImage(img)

    # Append the generated image to the dictionary for the current re_strength
    plot_images_dict[re_strength].append(img_tk)

# Function to display the current image
def display_plot():
    global current_image_idx, current_re_strength

    if current_re_strength in plot_images_dict and plot_images_dict[current_re_strength]:
        plot_label.config(image=plot_images_dict[current_re_strength][current_image_idx])
        plot_label.image = plot_images_dict[current_re_strength][current_image_idx]

# Function to navigate to the next plot
def next_plot():
    global current_image_idx, current_re_strength
    if current_re_strength in plot_images_dict and current_image_idx < len(plot_images_dict[current_re_strength]) - 1:
        current_image_idx += 1
        display_plot()

# Function to navigate to the previous plot
def previous_plot():
    global current_image_idx, current_re_strength
    if current_re_strength in plot_images_dict and current_image_idx > 0:
        current_image_idx -= 1
        display_plot()

# Function to handle the submission of the values and start the scan
def generate_scans():
    global mu_count_0, smup_mean, threshold_mean, threshold_dev, resiliences

    mu_count_0 = int(entry_mu_count.get())
    smup_mean = float(entry_smup_mean.get()) / 1000
    threshold_mean = float(entry_threshold_mean.get())
    threshold_dev = float(entry_threshold_dev.get())

    # Convert resiliences input to a list of floats
    resiliences = list(map(float, entry_resiliences.get().split(",")))

    # Perform the scan and store plots
    main()
    
    # Populate the dropdown with resiliences
    resiliences_combobox['values'] = resiliences  # Set the values for the dropdown
    if resiliences:  # Automatically select the first re_strength if available
        resiliences_combobox.current(0)
        select_re_strength()  # Display the first plot for the selected re_strength

# Function to select the re_strength to display
def select_re_strength():
    global current_re_strength, current_image_idx
    current_re_strength = float(resiliences_combobox.get())/100  # Get selected re_strength from the Combobox
    display_plot()  # Display the first plot

# Create the main application window
root = tk.Tk()
root.title("MUNE+")
root.geometry("1000x1000")

# Create a frame to hold the content and center it
frame = tk.Frame(root)
frame.pack(expand=True)

# Configure grid weight to center the content
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)

# Define labels and entry fields for each variable
labels = ["Motor Unit Count:",
          "Mean Motor Unit Amplitude (mV, ie: 62.5):",
          "Activation Threshold Mean (mA, ie: 26.5):",
          "Activation Threshold Deviation (mA, ie: 2):",
          "Resiliences (%, ie: 100, 60, 20)"]

entries = []

# Create and place labels and entries dynamically using grid()
for idx, label_text in enumerate(labels):
    label = tk.Label(frame, text=label_text)
    label.grid(row=idx, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(frame)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entries.append(entry)

# Create a label for the plot
plot_label = tk.Label(frame)
plot_label.grid(row=len(labels) + 1, columnspan=2, pady=10)

# Create a label for the resilience dropdown
label_resilience = tk.Label(frame, text="Select Resilience (%):")
label_resilience.grid(row=len(labels) + 2, column=0, padx=10, pady=5, sticky="e")  # Position it in the grid

# Create a Combobox for selecting re_strength
resiliences_combobox = ttk.Combobox(frame, values=[], state="readonly")
resiliences_combobox.grid(row=len(labels) + 2, column=1, pady=10)
resiliences_combobox.bind("<<ComboboxSelected>>", lambda event: select_re_strength())  # Bind selection event

# Assign each entry to a variable for easier access
entry_mu_count = entries[0]
entry_smup_mean = entries[1]
entry_threshold_mean = entries[2]
entry_threshold_dev = entries[3]
entry_resiliences = entries[4]

# Create a button to submit the form and generate scans
submit_button = tk.Button(frame, text="Generate Scans", command=generate_scans)
submit_button.grid(row=len(labels), columnspan=2, pady=20)

# Create navigation buttons to move between plots
previous_button = tk.Button(frame, text="Previous", command=previous_plot)
previous_button.grid(row=len(labels) + 3, column=0, pady=10)

next_button = tk.Button(frame, text="Next", command=next_plot)
next_button.grid(row=len(labels) + 3, column=1, pady=10)

# Start the Tkinter event loop
root.mainloop()