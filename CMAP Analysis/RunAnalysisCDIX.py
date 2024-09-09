from DataHandler import DataHandler
import numpy as np
import pandas as pd

def read_file_lines(filename):
    """Read the lines of a file and return them as a list."""
    with open(filename, 'rt') as file:
        return file.read().splitlines()

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


# CDIX

from CDIX import CDIX

thresholds=np.linspace(0.25,5,20)

def process_file(file):
    Data=DataHandler(f'DMScan/Multicentre 146/{file}.MEM')
    ThreshDict={}
    
    for threshold in thresholds:
        print("Starting", file, threshold)
        Values=CDIX(Data.x,Data.y,Mean_LS=threshold)
        Dict={'Gridsize':Values.G,
                'NDivs':Values.NDivs,
                'CDIX':Values.CDIX}
        ThreshDict[threshold]=Dict
        print("Finished",file,threshold,"With CDIX:",Values.CDIX)
    ThreshDict['Filename']=file
    df=pd.DataFrame(ThreshDict)
    return df, Data.name

for Cond in FileDict:
    path=f'DMScan_excel/CDIX/{Cond}.xlsx'
    ExcelWriter=pd.ExcelWriter(path)
    for file in FileDict[Cond]:
        df, dataname = process_file(file)
        df.to_excel(ExcelWriter, sheet_name=dataname)
    ExcelWriter.save()