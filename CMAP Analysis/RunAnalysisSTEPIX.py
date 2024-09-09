from DataHandler import DataHandler
import numpy as np
import pandas as pd

def read_file_lines(filename):
    """Read the lines of a file and return them as a list."""
    with open(filename, 'rt') as file:
        return file.read().splitlines()

#apb1=read_file_lines('DMScan/CA-EDM 9/CA-EDM-MSF2 APB-1 9.MEF')
#apb2=read_file_lines('DMScan/CA-EDM 9/CA-EDM-MSF2 APB-2 9.MEF')
#adm1=read_file_lines('DMScan/CA-EDM 9/CA-EDM-MSF2 ADM-1 9.MEF')
#adm2=read_file_lines('DMScan/CA-EDM 9/CA-EDM-MSF2 ADM-2 9.MEF')
#ta1=read_file_lines('DMScan/CA-EDM 9/CA-EDM-MSF2 TA-1 9.MEF')
#ta2=read_file_lines('DMScan/CA-EDM 9/CA-EDM-MSF2 TA-2 9.MEF')

apb1=read_file_lines('DMScan/Multicentre 146/MSF2 APB-1 146.MEF')
apb2=read_file_lines('DMScan/Multicentre 146/MSF2 APB-2 146.MEF')
adm1=read_file_lines('DMScan/Multicentre 146/MSF2 ADM-1 146.MEF')
adm2=read_file_lines('DMScan/Multicentre 146/MSF2 ADM-2 146.MEF')
ta1=read_file_lines('DMScan/Multicentre 146/MSF2 TA-1 146.MEF')
ta2=read_file_lines('DMScan/Multicentre 146/MSF2 TA-2 146.MEF')

FileDict={'APBV1':apb1,
          'APBV2':apb2,
          'ADMV1':adm1,
          'ADMV2':adm2,
          'TAV1':ta1,
          'TAV2':ta2,
}


# Stairfit

from STEPIX import SETPIX


thresholds=np.linspace(0.0025,0.05,20)


def process_file(file):
    Data=DataHandler(f'DMScan/Multicentre 146/{file}.MEM')
    ThreshDict={}
    
    for threshold in thresholds:
        print("Starting", file, threshold)
        Values=SETPIX(Data.y_trimmed, NoiseThreshold=threshold)
        Dict={'STEPIX':Values.STEPIX,
              'AMPIX':Values.AMPIX,
              'D50':Values.D50,
              'Point':Values.Point}
        ThreshDict[threshold]=Dict
        print("Finished",file,threshold,"With STEPIX:",Values.STEPIX)
    ThreshDict['Filename']=file
    df=pd.DataFrame(ThreshDict)
    return df, Data.name

for Cond in FileDict:
    path=f'DMScan_excel/STEPIX/{Cond}.xlsx'
    ExcelWriter=pd.ExcelWriter(path)
    for file in FileDict[Cond]:
        df, dataname = process_file(file)
        df.to_excel(ExcelWriter, sheet_name=dataname)
    ExcelWriter.save()