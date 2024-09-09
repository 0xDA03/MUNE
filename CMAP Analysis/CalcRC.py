import numpy as np
import pandas as pd

def ReadExcel(filename):
    data=pd.ExcelFile(filename)
    df = pd.read_excel(data,None)
    return df


def calc_RC(A):

    Vars=np.var(A,axis=0,ddof=1)
    WSVar=np.mean(Vars)
    SEM=np.sqrt(WSVar)
    CR=np.sqrt(2)*1.96*SEM
    return CR


import os
filelist = [f for f in os.listdir() if f.endswith('2.xlsx') or f.endswith('1.xlsx')]
print(filelist)

filenumber=0
while filenumber < len(filelist):


    DataV1=ReadExcel(filelist[filenumber])

    DataV2=ReadExcel(filelist[filenumber+1])

    path=f'Stats/{filelist[filenumber][:2]}_RC.xlsx'

    filenumber+=2

    NameList=list(DataV1)
    HeadList=list(DataV1[NameList[0]])
    ParamList=list(DataV1[NameList[0]][HeadList[0]])

    # For STEPIX and Stairfit:
    ParamList=ParamList[:-1]
    ThreshDict={}

    for threshold in HeadList[1:-1]:
        ParamsDict={}
        V1Arr=[]
        V2Arr=[]
        for Name in NameList:
            NameV1 = Name
            NameV2 = Name[:-2]+".2"
            V1Arr.append(DataV1[NameV1][threshold].to_numpy().ravel())
            V2Arr.append(DataV2[NameV2][threshold].to_numpy().ravel())
        
        V1Arr=np.array(V1Arr).transpose()
        V2Arr=np.array(V2Arr).transpose()
        for i in range(len(ParamList)):

            a=V1Arr[i].astype('float64')
            b=V2Arr[i].astype('float64')

            non_nan_indices = np.logical_and(~np.isnan(a), ~np.isnan(b))

            a = a[non_nan_indices]
            b = b[non_nan_indices]

            A=np.stack([a,b])
            R=calc_RC(A)
            ParamsDict[ParamList[i]]=R
        ThreshDict[threshold]=ParamsDict

    ExcelWriter=pd.ExcelWriter(path)

    df=pd.DataFrame(ThreshDict)
    df.to_excel(ExcelWriter)
    ExcelWriter.save()