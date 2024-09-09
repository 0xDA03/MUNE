from DataHandler import DataHandler
import numpy as np
import pandas as pd

def read_file_lines(filename):
    """Read the lines of a file and return them as a list."""
    with open(filename, 'rt') as file:
        return file.read().splitlines()

#apb1=read_file_lines('DMScan/Multicentre 146/MSF2 APB-1 146.MEF')
#apb2=read_file_lines('DMScan/Multicentre 146/MSF2 APB-2 146.MEF')
#adm1=read_file_lines('DMScan/Multicentre 146/MSF2 ADM-1 146.MEF')
#adm2=read_file_lines('DMScan/Multicentre 146/MSF2 ADM-2 146.MEF')
ta1=read_file_lines('DMScan/Multicentre 146/MSF2 TA-1 146.MEF')
ta2=read_file_lines('DMScan/Multicentre 146/MSF2 TA-2 146.MEF')

FileDict={#'APBV1':apb1,
          #'APBV2':apb2,
          #'ADMV1':adm1,
          #'ADMV2':adm2,
          'TAV1':ta1,
          'TAV2':ta2,
}


# Stairfit

from Stairfit import Stairfit

from multiprocessing import Pool

thresholds = np.linspace(0.010,0.020,3) # typical (0.005,0.025,5) but not working for TA


def process_file(file):
    Data=DataHandler(f'DMScan/Multicentre 146/{file}.MEM')
    ThreshDict={}
    

    for threshold in thresholds:
        print("Starting", file, threshold)
        Values=Stairfit(Data.x, Data.y, termination_threshold=threshold)
        Dict={'MUNE':Values.M,
              'Diff':Values.Diff}
        ThreshDict[threshold]=Dict
        print("Finished",file,threshold,"With MUNE:",Values.M)
    ThreshDict['Filename']=file
    df=pd.DataFrame(ThreshDict)
    return df, Data.name


if __name__ == '__main__':
    thresholds = np.linspace(0.010,0.020,3) # typical (0.005,0.025,5) but not working for TA

    for Cond in FileDict:
        path=f'DMScan_excel/Stairfit/{Cond}.xlsx'
        ExcelWriter = pd.ExcelWriter(path)

        # Initialize the pool and run the processing
        with Pool() as p:
            results = p.map(process_file, FileDict[Cond])
        
        print(f"Finished pool, writing {Cond} file")
        # Write the results to Excel
        for df, sheet_name in results:
            df.to_excel(ExcelWriter, sheet_name=sheet_name)
        
        ExcelWriter.save()