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

DIR_IN = "ANALYSIS/MEM-RS1.65"                      #### EDIT THIS DEPENDING ON DATASET PROPERTIES
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
    for path in paths:
        df = pd.read_csv(f"{DIR_IN}/{path}/MSUE (µV).csv", index_col=0)
        sd_str = ''
        cov_str = ''
        sdc_str = ''
        sdcp_str = ''
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
        with open(f"{DIR_IN}/{path}/SDpyMSUE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
            file.write(sd_str)
        with open(f"{DIR_IN}/{path}/COVpyMSUE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
            file.write(cov_str)
        with open(f"{DIR_IN}/{path}/SDCpyMSUE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
            file.write(sdc_str)
        with open(f"{DIR_IN}/{path}/SDCPpyMSUE.csv", 'w') as file:
            file.write("5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
            file.write(sdcp_str)
        sd_str_combined += f"{path},{sd_str}\n" 
        cov_str_combined += f"{path},{cov_str}\n"
        sdc_str_combined += f"{path},{sdc_str}\n"
        sdcp_str_combined += f"{path},{sdcp_str}\n"
    with open(f"{DIR_IN}/SDpyMSUE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
        file.write(sd_str_combined)
    with open(f"{DIR_IN}/COVpyMSUE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
        file.write(cov_str_combined)
    with open(f"{DIR_IN}/SDCpyMSUE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
        file.write(sdc_str_combined)
    with open(f"{DIR_IN}/SDCPpyMSUE.csv", 'w') as file:
        file.write(", 5MU, 10MU, 20MU, 40Mu, 80MU, 160MU\n")
        file.write(sdcp_str_combined)

sdc(PATHS)