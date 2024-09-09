import numpy as np
import pandas as pd

def ReadExcel(filename):
    data=pd.ExcelFile(filename)
    df = pd.read_excel(data,None)
    return df


def calc_ICC(A):
    (k,n)= A.shape
    if k>2:
        print("Flip the array")
        return
    SStotal = np.var(A,ddof=1) * (n*k - 1)
    MSR = np.var(np.mean(A,0),ddof=1) * k
    MSW = np.sum(np.var(A,axis=0,ddof=1)) / n
    MSC = np.var(np.mean(A,1),ddof=1) * n
    MSE = (SStotal - MSR *(n - 1) - MSC * (k -1))/ ((n - 1) * (k - 1))

    r = (MSR - MSE) / (MSR + (k-1)*MSE + k*(MSC-MSE)/n)
    return r


import os
filelist = [f for f in os.listdir() if f.endswith('.xlsx')]
print(filelist)

filenumber=0
while filenumber < len(filelist):


    DataV1=ReadExcel(filelist[filenumber])

    DataV2=ReadExcel(filelist[filenumber+1])

    path=f'Stats/{filelist[filenumber][:2]}_ICC.xlsx'
    print(path)

    filenumber+=2

    NameList=list(DataV1)
    HeadList=list(DataV1[NameList[0]])
    ParamList=list(DataV1[NameList[0]][HeadList[0]])
    

    # For STEPIX and Stairfit:
    if ParamList[0] != "Gridsize":
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
            #print(A)
            R=calc_ICC(A)
            #print(R)
            ParamsDict[ParamList[i]]=R
        ThreshDict[threshold]=ParamsDict

    ExcelWriter=pd.ExcelWriter(path)

    df=pd.DataFrame(ThreshDict)
    df.to_excel(ExcelWriter)
    ExcelWriter.save()