""" 
    The aim is to model and simulate different physiological conditions of motor neuron degeneration and remodeling,
    generating CMAP scans throughout the process to assess the accuracy and reliability of MUNE fitting using MScanFit.
"""

import numpy as np
from scipy.stats import expon
from scipy.special import erf
from Export import *

# SIMULATION PARAMETERS
SEEDS = list(range(1,11))           # seeds for pseudo-random reproducability, one per model individual
DE_METHODS = [                      # motor neuron degeneration methods characterized by:
                "random",           # random degeneration
                "selective"         # large-biased degeneration (selective vulnerability)
            ]
RE_METHODS = [                      # collateral reinnervation methods characterized by:
                "random",           # compensation via random motor units
                "distributive",     # compensation via distributive (evenly amongst all remaining) motor units
                "selective",        # compensation via selective (large-biased) motor units
                "none",             # no compensation
            ]
RESILIENCE = [
                0.2,
                0.6]                # resilience is the fraction of degenerated nerves that are to be compensated for
VULNERABILITY = 0.5                 # vulnerability represents the fraction of units denervated per step
SAMPLES = 500                       # length of simulation (nsamples)
FLANKS = 20                         # length of pre-scan and post-scan limit region
NOISE = 0.01                        # additive noise deviation

# MOTOR POOL PARAMETERS
MU_COUNT = 160                  # number of motor units in the initial pool
SMUP_MEAN = 0.0625              # single motor unit potential amplitude mean (mV)
SMUP_MIN = 0.025                # single motor unit potential amplitude minimum (mV)
THRESHOLD_MEAN = 10.683675      # activation threshold mean (mA)
THRESHOLD_DEV = 2               # activation threshold deviation (gaussian) (mA)
THRESHOLD_SPREAD = 0.0165       # relative spread of threshold


def main():
    for de_method in DE_METHODS:
        for re_method in RE_METHODS:
            for resilience in RESILIENCE:
                gen_path = f"de-{de_method}/re-{re_method}/str-{resilience}"    # generic path to store files
                mef_paths = []                                                  # will store the MEM files that wil be referenced in the MEF index

                for i in range(len(SEEDS)):
                    rng = np.random.default_rng(seed=SEEDS[i])                                                          # set the seed of the rng for reproducability
                    mu_sizes = expon.rvs(scale=SMUP_MEAN-SMUP_MIN, loc=SMUP_MIN, size=MU_COUNT, random_state=rng)       # intialize the healthy motor pool with  given mean amplitude
                    mu_thresholds = rng.normal(THRESHOLD_MEAN, THRESHOLD_DEV, len(mu_sizes))                            # produce a normal distribution of motor unit thresholds
                    mu_devs = mu_thresholds * THRESHOLD_SPREAD                                                          # calculate deviations for each motor unit threshold
                    mu_dict = list(zip(mu_sizes, mu_thresholds, mu_devs))                                               # zip motor unit properties to facilitate synced remodeling
                    mu_counts = []                                                                                      # keep track of motor pool sizes for trajectories
                    max_cmaps = []                                                                                      # keep track of maximal CMAP for trajectories

                    while len(mu_dict) >= 5:
                        mu_sizes, mu_thresholds, mu_devs = [np.array(x) for x in zip(*mu_dict)]     # unzip motor unit properties for easier scanning
                        mu_count = len(mu_dict)
                        mu_counts.append(mu_count)

                        stimuli, responses = scan(mu_sizes, mu_thresholds, mu_devs, rng)            # generate the (stimulus,response) data for the scan
                        # generatePlot(f"{gen_path}/mu-{mu_count}", i+1 , stimuli, responses)         # plot and save the (stimulus,response) data from the scan in /PLOTS
                        generateMEM(gen_path, f"{mu_count}-{i+1}", stimuli, responses)              # export scan data to MScanFit-compatible .MEM file in /MEM
                        # generateTXT(f"{gen_path}/mu-{mu_count}", i+1, mu_thresholds, mu_sizes)      # export motor unit threshold, size ground truths to .txt file in /RAW
                        # generateDist(f"{gen_path}/mu-{mu_count}", i+1, mu_sizes)                    # plot frequency distribution for the SMUPs
                        # mef_paths.append(f"{mu_count}-{i+1}")                                       # keep track of the MEM filenames for the MEF index
                        # max_cmaps.append(max(responses))                                            # store the maximal CMAP response for the trajectories

                        mu_dict = degenerate(mu_dict, de_method, re_method, resilience, rng)     # handle degeneration and reinnervation of motor units

                    # generateTrajectory(f"{gen_path}/mu-{mu_count}", i+1, mu_counts, max_cmaps)      # generate trajectory based on change in maximal CMAP over degeneration progress

                    re_str = resilience*100 if re_method != "none" else "0.0"                                                                       # string helper for progress bar                           
                    print_progress(i+1, len(SEEDS), f"Running '{de_method}' denervation and {re_str}% '{re_method}' reinnervation", '', 0, 50)      # display progress bar
                
                # generateMEF(gen_path, mef_paths)    # create the MEF index for all MEM files produced in the given condition

                if re_method == "none":
                    break   # break unnecessary loop of varying reinnervation strengths when there is no compensation 


def scan(mu_sizes, mu_thresholds, mu_devs, rng):
    """ Generate stimulus,response CMAP data given a motor pool """

    stimuli = np.geomspace(min(mu_thresholds)-0.5, max(mu_thresholds)+0.5, SAMPLES)     # produce a geometric sequence of stimulus amplitudes
    stimuli = np.concatenate([
        np.repeat(min(mu_thresholds)-0.5, FLANKS),
        stimuli,
        np.repeat(max(mu_thresholds)+0.5, FLANKS)
    ])
    # showPlot(x=None, y=stimuli)
    noise = rng.normal(0, NOISE, SAMPLES+2*FLANKS)                                               # generate random noise variabilities
    # showPlot(x=None, y=noise)                                             
    # plot_activation_curves(stimuli, mu_thresholds, mu_devs)
    responses = []
    for stimulus in stimuli:
        probabilities = (erf((1/(np.sqrt(2)*np.array(mu_devs)))*(stimulus-mu_thresholds))+1)/2      # calculate the firing probability for each motor unit given a stimulus
        activations = rng.uniform(0, 1, len(mu_sizes)) <= probabilities                             # determine the binary firing of each motor unit
        responses.append(np.sum(mu_sizes * (activations.astype(int))))                              # calculate the CMAP response of all motor units that fired                                                  
    responses = np.array(responses) + noise                                                         # incorporate random noise variation to the CMAPs

    return stimuli, responses


def degenerate(mu_dict, de_method, re_method, resilience, rng):
    """ Handle the degeneration and reinnervation of motor units """

    if de_method == "random":
        de_dict = [tuple(x) for x in rng.choice(mu_dict, size=int(len(mu_dict)*VULNERABILITY), replace=False)]      # randomly select X% of the motor units to degenerate

    elif de_method == "selective":
        mu_dict = sorted(mu_dict, key=lambda x: x[0])               # sort the motor units by size
        de_dict = mu_dict[int(len(mu_dict) * VULNERABILITY):]       # denervate the largest motor units

    mu_dict = list(set(mu_dict) - set(de_dict))                             # remove these degenerated units from the modeled units
    mu_sizes, mu_thresholds, mu_devs = [list(x) for x in zip(*mu_dict)]     # unzip remaining motor unit properties to facilitate reinnervation calculations
    de_sizes, de_thresholds, de_devs = [list(x) for x in zip(*de_dict)]     # unzip denervated motor unit properties to facilitate reinnervation calculations
    
    if re_method == "random":
        re_sizes = rng.choice(de_sizes, size=int(len(de_sizes)*resilience), replace=False)                          # randomly select some % of the degenerated units to reinnervate           
        re_indices = rng.choice(list(range(len(mu_sizes))), size=int(len(de_sizes)*resilience), replace=False)      # randomly select some % of the remaining units to compensate
        for i in range(len(re_sizes)):                                                                                       
            mu_sizes[re_indices[i]] += re_sizes[i]                                                                  # compensate remaining motor units

    elif re_method == "distributive":                                 
            re_amplitude = sum(de_sizes) * resilience / len(mu_sizes)       # calculate equal fraction of total CMAP attributable to denervated units
            for i in range(len(mu_sizes)):
                mu_sizes[i] += re_amplitude                                 # compensate each motor unit equally

    elif re_method == "selective":
            de_sum = sum(de_sizes)                                                      # total CMAP response attributable to denervated units 
            mu_squares = np.square(mu_sizes)                                            # square motor unit sizes to get a more exponential distribution
            mu_square_sum = np.sum(mu_squares)
            for i in range(len(mu_sizes)):          
                mu_sizes[i] += (mu_squares[i] / mu_square_sum * de_sum * resilience)    # compensate the largest remaining motor units by the largest amount

    return list(zip(mu_sizes, mu_thresholds, mu_devs))      # rezip motor unit properties to facilitate synced remodeling again


def print_progress (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()

def plot_activation_curves(stimuli, mu_thresholds, mu_devs):
    """
    Visualizes the activation probability curve for each motor unit.
    Each S-shaped curve represents a single motor unit's probability of firing
    as the stimulus intensity increases.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calculate and plot the probability curve for each motor unit
    for i in range(len(mu_thresholds)):
        threshold = mu_thresholds[i]
        dev = mu_devs[i]
        
        # This is the same calculation from your scan() function
        probabilities = (erf((1 / (np.sqrt(2) * dev)) * (stimuli - threshold)) + 1) / 2
        
        # Plot the curve for the current motor unit
        # Use a low alpha to see overlapping curves
        ax.plot(stimuli, probabilities, color='blue', alpha=0.3)

    ax.set_title(f'Activation Probability Curves for {len(mu_thresholds)} Motor Units')
    ax.set_xlabel('Stimulus Amplitude (mA)')
    ax.set_ylabel('Probability of Firing P(fire)')
    ax.set_ylim(0, 1)
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.show()

main()