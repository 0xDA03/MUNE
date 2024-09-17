""" 
    The aim is to replicate the probabilistic MUNE algorithm described by Bostock in his 2015 paper 
    titled "Estimating motor Unit Numbers From a CMAP Scan", wherein preliminary models of collateral
    reinnvervation are simulated and then fitted using MSCanFit
"""

import os
import numpy as np
from scipy.stats import expon
from scipy.special import erf
import plotly.graph_objects as graph
from Export import generateDAT
from datetime import datetime


def generate_sizes():
    # Attempt to replicate the MU amplitudes of the 60 target scans produced by Bostock, using modeled reinnervation

    SEEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    data = [[]]*10

    for i in range(10):
        rng = np.random.default_rng(seed=SEEDS[i])                                          # set the seed of the rng for reproducability
        mu_sizes = expon.rvs(scale=0.0625-0.025, loc=0.025, size=160, random_state=rng)     # intialize the healthy model with 160 units with a given mean amplitude

        while len(mu_sizes) >= 5:
            mu_count = len(mu_sizes)
            data[i].append({"mu_count": mu_count, "mu_mean": np.mean(mu_sizes), "mu_sizes": mu_sizes})
            # print(f"Mean single unit amplitude for {mu_count} motor units: {np.mean(mu_sizes)}")
            
            de_sizes = rng.choice(mu_sizes, size=int(mu_count*0.5), replace=False)                      # randomly select 50% of the motor units to degenerate
            mu_sizes = np.setdiff1d(mu_sizes, de_sizes, assume_unique=True)                             # remove these degenerated units from the modeled units
            re_sizes = rng.choice(de_sizes, size=int(mu_count*0.3), replace=False)                      # randomly select 60% of the degenerated units (30% of total) to reinnervate
            re_indices = rng.choice(list(range(len(mu_sizes))), size=int(mu_count*0.3), replace=False)  # randomly select 60% of the remaining units (30% of total) to compensate
            
            for j in range(len(re_sizes)):
                mu_sizes[re_indices[j]] += re_sizes[j]      # compensate remaining motor units
    
    return data


def generate_scan(mu_sizes):
    # Generate stimulus,response data given MU sizes
    
    THRESHOLD_MEAN = 26.5           # Activation threshold mean
    THRESHOLD_DEV = 2               # Activation threshold deviation (gaussian)
    THRESHOLD_SPREAD = 0.0165       # Relative spread
    SAMPLES = 450                   # Length of simulation (nsamples)
    NOISE = 0.005                   # Additive noise deviation

    rng = np.random.default_rng(seed=1)                                     # set the seed of the rng for reproducability
    mu_count = len(mu_sizes)                                                # get the number of motor units
    mu_thresholds = rng.normal(THRESHOLD_MEAN, THRESHOLD_DEV, mu_count)     # produce a normal distribution of motor unit thresholds
    mu_devs = mu_thresholds * THRESHOLD_SPREAD                              # calculate deviations for each motor unit threshold
    stimuli = np.linspace(20, 33, SAMPLES)                                  # produce a linear sequence of stimulus amplitudes
    noise = rng.normal(0, NOISE, SAMPLES)
    
    responses = []
    for stimulus in stimuli:
        probabilities =  (erf((1/(np.sqrt(2)*mu_devs))*(stimulus-mu_thresholds))+1)/2       # calculate the firing probability for each motor unit with respect to a stimulus
        activations = rng.uniform(0, 1, mu_count) <= probabilities                          # determine the binary firing of each motor unit
        cmap = np.sum(mu_sizes * (activations.astype(int)))                                 # calculate the CMAP response of all motor units that fired                                                  # incorporate some random noise variation
        responses.append(cmap)
    
    responses = np.array(responses) + noise     
    return stimuli, responses
    

def plot_scan(stimuli, responses, mu_count, mu_mean):
    # Plot the stimulus,response curve given MU sizes

    fig = graph.Figure()
    fig.add_trace(graph.Scatter(x=stimuli, y=responses, mode="markers"))

    directory = f"PLOTS/Bostock/{mu_count}"                         # get an appropriate path to store the plot
    os.makedirs(directory, exist_ok=True)                           # ensure all intermediate directories are created
    fig.write_image(f"PLOTS/Bostock/{mu_count}/{mu_mean}.png")     # save the plot to the specified path


data = generate_sizes()
for i in range(len(data)):
    for j in range(len(data[i])):
        stimuli, responses =  generate_scan(data[i][j]["mu_sizes"])
        plot_scan(stimuli, responses, data[i][j]["mu_count"], data[i][j]["mu_mean"])
        generateDAT("Bostock", f"{data[i][j]['mu_count']}-{data[i][j]['mu_mean']}", stimuli, responses)


# Export data to MScanFit-compatible .DAT file
