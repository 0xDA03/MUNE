import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

DIR_IN = "N30/ANALYSIS/MEM-Nov3"                      #### EDIT THIS DEPENDING ON DATASET PROPERTIES
PATHS = []

for de_condition in DE_CONDITIONS:
    for re_condition in RE_CONDITIONS:
        if re_condition == "none":
                PATHS.append(f"de-{de_condition}/re-{re_condition}/str-0.2")
                break
        for str_condition in STR_CONDITIONS:
            PATHS.append(f"de-{de_condition}/re-{re_condition}/str-{str_condition}")

def sdc(paths):
    sd_str_combined = ''
    cov_str_combined = ''
    sdc_str_combined = ''
    sdcp_str_combined = ''
    sem_str_combined = ''
    semp_str_combined = ''
    for path in paths:
        df = pd.read_csv(f"{DIR_IN}/{path}/MUNE.csv", index_col=0)
        sd_str = ''
        cov_str = ''
        sdc_str = ''
        sdcp_str = ''
        sem_str = ''
        semp_str = ''
        for i in df:
            col = df.filter([i]).values
            mean = np.mean(col)
            var = np.var(col, ddof=1)
            sd = np.sqrt(var)
            sd_str += f"{sd},"
            cov = sd/mean
            cov_str += f"{cov},"
            sdc = sd * np.sqrt(2) * 1.96
            sdc_str += f"{sdc},"
            sdcp = sdc/mean
            sdcp_str += f"{sdcp},"
            # sem = 
            # sem_str += f"{sem},"
            # semp = sem/mean
            # semp_str += f"{semp},"
        with open(f"{DIR_IN}/{path}/SDpyMUNE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
            file.write(sd_str)
        with open(f"{DIR_IN}/{path}/COVpyMUNE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
            file.write(cov_str)
        with open(f"{DIR_IN}/{path}/SDCpyMUNE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
            file.write(sdc_str)
        with open(f"{DIR_IN}/{path}/SDCPpyMUNE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
            file.write(sdcp_str)
        with open(f"{DIR_IN}/{path}/SEMpyMUNE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
            file.write(sem_str)
        with open(f"{DIR_IN}/{path}/SEMpyMUNE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
            file.write(semp_str)
        sd_str_combined += f"{path},{sd_str}\n" 
        cov_str_combined += f"{path},{cov_str}\n"
        sdc_str_combined += f"{path},{sdc_str}\n"
        sdcp_str_combined += f"{path},{sdcp_str}\n"
        sem_str_combined += f"{path},{sem_str}\n"
        sem_str_combined += f"{path},{semp_str}\n"
    with open(f"{DIR_IN}/SDpyMUNE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
        file.write(sd_str_combined)
    with open(f"{DIR_IN}/COVpyMUNE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
        file.write(cov_str_combined)
    with open(f"{DIR_IN}/SDCpyMUNE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
        file.write(sdc_str_combined)
    with open(f"{DIR_IN}/SDCPpyMUNE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
        file.write(sdcp_str_combined)
    with open(f"{DIR_IN}/SEMpyMUNE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
        file.write(sem_str_combined)
    with open(f"{DIR_IN}/SEMpyMUNE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40MU, 80MU, 160MU\n")
        file.write(semp_str_combined)

sdc(PATHS)