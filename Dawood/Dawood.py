""" 
    The aim is to replicate the probabilistic MUNE algorithm described by Bostock in his 2015 paper 
    titled "Estimating motor Unit Numbers From a CMAP Scan", wherein preliminary models of collateral
    reinnvervation are simulated and then fitted using MSCanFit. Then, we test different methods of
    collateral reinnervation.
"""

import numpy as np
from scipy.stats import expon
from scipy.special import erf
from Export import generateDAT, generateTXT, generatePlot, generateMEM, generateMEF, generateTrajectory


def main():
    SEEDS = list(range(1,11))                   # seeds for pseudo-random reproducability
    DE_METHODS = [                              # motor neuron degeneration methods characterized by:
                    # "random",                   # random degeneration
                    "selective"                 # large-biased degeneration (selective vulnerability)
                ]
    RE_METHODS = [                              # collateral reinnervation methods characterized by:
                    # "random",                   # compensation via random motor units
                    # "selective",                # compensation via selective (large-biased) motor units
                    # "none",                     # no compensation
                    "distributed"
                ]
    RE_STRENGTHS = [0.6]                # strength of reinnervation represents the fraction of degenerated nerves that are to be compensated for
    DE_STRENGTH = 0.5

    for de_method in DE_METHODS:
        for re_method in RE_METHODS:
            for re_strength in RE_STRENGTHS:

                gen_path = f"de-{de_method}/re-{re_method}/str-{re_strength}"       # generic path to store files
                mef_paths = []                                                      # will store the MEM files that wil be referenced in the MEF index

                for i in range(len(SEEDS)):
                    rng = np.random.default_rng(seed=SEEDS[i])                                          # set the seed of the rng for reproducability
                    mu_sizes = expon.rvs(scale=0.0625-0.025, loc=0.025, size=160, random_state=rng)     # intialize the healthy model with 160 units and a given mean amplitude
                    mu_sizes = np.sort(mu_sizes)
                    mu_counts = []                                                        # sort the mtor units by size
                    max_CMAPs = []

                    while len(mu_sizes) >= 5:
                        mu_count = len(mu_sizes)        # motor unit count
                        mu_counts.append(mu_count)
                        mu_mean = np.mean(mu_sizes)     # mean single unit amplitude

                        stimuli, responses = scan(mu_sizes, rng)                          # generate the (stimulus,response) data for the scan
                        max_CMAPs.append(max(responses))
                        generatePlot(f"{gen_path}/mu-{mu_count}", mu_mean, stimuli, responses)      # plot and save the (stimulus,response) data from the scan in /PLOTS
                        # generateDAT(gen_path, f"{mu_count}-{mu_mean}", stimuli, responses)          # export scan data to MScanFit-compatible .DAT file in /DAT
                        generateMEM(gen_path, f"{mu_count}-{mu_mean}", stimuli, responses)          # export scan data to MScanFit-compatible .MEM file in /MEM
                        generateTXT(f"{gen_path}/mu-{mu_count}", mu_mean, mu_sizes)                 # export motor unit size raw data to .txt file in /RAW
                        mef_paths.append(f"{mu_count}-{mu_mean}")                                   # keep track of the MEM filenames for the MEF index
                        
                        mu_sizes = degenerate(mu_sizes, mu_count, de_method, re_method, re_strength, DE_STRENGTH, rng)      # handle degeneration and reinnervation of motor units
                    
                    generateTrajectory(f"{gen_path}/mu-{mu_count}", mu_mean, mu_counts, max_CMAPs)

                    re_str = re_strength*100 if re_method != "none" else "0.0"                                   
                    print_progress(i+1, len(SEEDS), f"Running '{de_method}' deinnervation and {re_str}% '{re_method}' reinnervation", '', 0, 50)     # display progress bar
                
                generateMEF(gen_path, mef_paths)

                if re_method == "none":
                    break   # break unnecessary loop of varying reinnervation strengths when there is no compensation 


def degenerate(mu_sizes, mu_count, de_method, re_method, re_strength, de_strength, rng):
    # Handle the degeneration and reinnervation of motor units

    if de_method == "random":
        de_sizes = rng.choice(mu_sizes, size=int(mu_count*de_strength), replace=False)      # randomly select X% of the motor units to degenerate

    elif de_method == "selective":
        mu_sizes = np.sort(mu_sizes)                # sort the motor units by size
        de_sizes = mu_sizes[int(mu_count * de_strength):]     # denervate the largest motor units
    
    mu_sizes = np.setdiff1d(mu_sizes, de_sizes, assume_unique=True)     # remove these degenerated units from the modeled units
   
    if re_method == "random":
        re_sizes = rng.choice(de_sizes, size=int(mu_count*re_strength*de_strength), replace=False)                          # randomly select X% of the degenerated units to reinnervate
        re_indices = rng.choice(list(range(len(mu_sizes))), size=int(mu_count*re_strength*de_strength), replace=False)      # randomly select X% of the remaining units to compensate
        for i in range(len(re_sizes)):
            mu_sizes[re_indices[i]] += re_sizes[i]                                                                  # compensate remaining motor units

    elif re_method == "selective":
        re_sizes = rng.choice(de_sizes, size=int(mu_count*re_strength*de_strength), replace=False)      # randomly select X% of the degenerated units to reinnervate
        re_sizes = np.sort(re_sizes)                                                            # sort the motor units to be reinnervated by size
        mu_sizes = np.sort(mu_sizes)                                                            # sort the remaining motor units by size
        for i in range(len(re_sizes)):
            i = -(i+1)
            mu_sizes[i] += re_sizes[i]                                                          # compensate the largest remaining motor units by the largest amount

    elif re_method == "distributed":
        de_sum = np.sum(de_sizes)
        re_amplitude = de_sum * re_strength / len(mu_sizes)
        for i in range(len(mu_sizes)):
            mu_sizes[i] += re_amplitude

    return mu_sizes


def scan(mu_sizes, rng):
    # Generate stimulus,response data given MU sizes
    
    THRESHOLD_MEAN = 26.5           # Activation threshold mean
    THRESHOLD_DEV = 2               # Activation threshold deviation (gaussian)
    THRESHOLD_SPREAD = 0.0165       # Relative spread
    SAMPLES = 450                   # Length of simulation (nsamples)
    NOISE = 0.01                    # Additive noise deviation

    mu_count = len(mu_sizes)                                                # get the number of motor units
    mu_thresholds = rng.normal(THRESHOLD_MEAN, THRESHOLD_DEV, mu_count)     # produce a normal distribution of motor unit thresholds
    mu_devs = mu_thresholds * THRESHOLD_SPREAD                              # calculate deviations for each motor unit threshold
    stimuli = np.linspace(20, 33, SAMPLES)                                  # produce a linear sequence of stimulus amplitudes
    noise = rng.normal(0, NOISE, SAMPLES)                                   # generate random noise variabilities
    
    responses = []
    for stimulus in stimuli:
        probabilities =  (erf((1/(np.sqrt(2)*mu_devs))*(stimulus-mu_thresholds))+1)/2       # calculate the firing probability for each motor unit with respect to a stimulus
        activations = rng.uniform(0, 1, mu_count) <= probabilities                          # determine the binary firing of each motor unit
        cmap = np.sum(mu_sizes * (activations.astype(int)))                                 # calculate the CMAP response of all motor units that fired                                                  
        responses.append(cmap)
    responses = np.array(responses) + noise                                                 # incorporate random noise variation to the CMAPs

    return stimuli, responses


def print_progress (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    if iteration == total: 
        print()


main()