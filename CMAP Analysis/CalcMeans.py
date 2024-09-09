import numpy as np
import pandas as pd

def ReadExcel(filename):
    data=pd.ExcelFile(filename)
    df = pd.read_excel(data,None)
    return df


def calc_all(A):
    mean=np.mean(A)
    std=np.std(A)
    coeffvar=std/mean
    median=np.median(A)
    IQR=np.subtract(*np.percentile(A, [75, 25]))
    IQR_CV=IQR/median
    return mean,std,coeffvar,median,IQR,IQR_CV


import os
filelist = [f for f in os.listdir() if f.endswith('.xlsx')]
print(filelist)

filenumber=0
while filenumber < len(filelist):


    DataV1=ReadExcel(filelist[filenumber])

    DataV2=ReadExcel(filelist[filenumber+1])

    path=f'Stats/{filelist[filenumber][:2]}_Means.xlsx'

    filenumber+=2

    NameList=list(DataV1)
    HeadList=list(DataV1[NameList[0]])
    ParamList=list(DataV1[NameList[0]][HeadList[0]])

    # For STEPIX and Stairfit:
    ParamList=ParamList[:-1]

    # Initialize separate dictionaries for each statistic
    MeanDict = {}
    StdDict = {}
    CoeffVarDict = {}
    MedianDict = {}
    IQRDict = {}
    IQRCVDict = {}

    for threshold in HeadList[1:-1]:
        ParamsMeanDict = {}
        ParamsStdDict = {}
        ParamsCoeffVarDict = {}
        ParamsMedianDict = {}
        ParamsIQRDict = {}
        ParamsIQRCVDict = {}
        
        V1Arr=[]
        V2Arr=[]
        for Name in NameList:
            NameV1 = Name
            NameV2 = Name[:-2]+".2"
            V1Arr.append(DataV1[NameV1][threshold].to_numpy().ravel())
            V2Arr.append(DataV2[NameV2][threshold].to_numpy().ravel())

        V1Arr = np.array(V1Arr).transpose()
        V2Arr = np.array(V2Arr).transpose()
        for i in range(len(ParamList)):
            a = V1Arr[i].astype('float64')
            b = V2Arr[i].astype('float64')

            non_nan_indices = np.logical_and(~np.isnan(a), ~np.isnan(b))

            a = a[non_nan_indices]
            b = b[non_nan_indices]

            A = np.stack([a, b])
            R = calc_all(A)

            ParamsMeanDict[ParamList[i]] = R[0]
            ParamsStdDict[ParamList[i]] = R[1]
            ParamsCoeffVarDict[ParamList[i]] = R[2]
            ParamsMedianDict[ParamList[i]] = R[3]
            ParamsIQRDict[ParamList[i]] = R[4]
            ParamsIQRCVDict[ParamList[i]] = R[5]

        MeanDict[threshold] = ParamsMeanDict
        StdDict[threshold] = ParamsStdDict
        CoeffVarDict[threshold] = ParamsCoeffVarDict
        MedianDict[threshold] = ParamsMedianDict
        IQRDict[threshold] = ParamsIQRDict
        IQRCVDict[threshold] = ParamsIQRCVDict

    ExcelWriter = pd.ExcelWriter(path)

    # Write each dictionary to a separate sheet in the Excel file
    pd.DataFrame(MeanDict).to_excel(ExcelWriter, sheet_name="Mean")
    pd.DataFrame(StdDict).to_excel(ExcelWriter, sheet_name="Std")
    pd.DataFrame(CoeffVarDict).to_excel(ExcelWriter, sheet_name="Coeff_Var")
    pd.DataFrame(MedianDict).to_excel(ExcelWriter, sheet_name="Median")
    pd.DataFrame(IQRDict).to_excel(ExcelWriter, sheet_name="IQR")
    pd.DataFrame(IQRCVDict).to_excel(ExcelWriter, sheet_name="IQR_CV")

    ExcelWriter.save()
