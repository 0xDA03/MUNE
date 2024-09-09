from DataHandler import DataHandler
import os

filelist = [f for f in os.listdir() if f.endswith('.MEM')]
#print(filelist)


Diction={}

for file in filelist:
    Data=DataHandler(file)
    if Data.name in Diction:
        Diction[Data.name].append(file)
    else:
        Diction[Data.name] = [file]

Diction = {k: Diction[k] for k in sorted(Diction.keys())}

print(len(Diction))
print(Diction)

filenames=[]
for i in Diction:
    filenames.extend(Diction[i])


print(filenames)

V1=filenames[::2]
V2=filenames[1::2]

with open('Beth.MEF', 'w') as fp:
    for item in V1:
        # write each item on a new line
        fp.write("%s\n" % item[:-4])
    for item in V2:
        # write each item on a new line
        fp.write("%s\n" % item[:-4])
    print('Done')

## Code below useful in RunAnalysis for finding and sorting names

# FileDict={}

# filenames2=[]
# for i in FileDict0:
#     Diction={}
#     filelist=FileDict0[i]
#     for file in filelist:
#         Data=DataHandler(f"MEM/Bin Ge/{file}.MEM")
#         if Data.name in Diction:
#             Diction[Data.name].append(file)
#         else:
#             Diction[Data.name] = [file]
#     Diction = {k: Diction[k] for k in sorted(Diction.keys())}
#     filenames=[]
#     for j in Diction:
#         filenames.extend(Diction[j])
#     FileDict[i]=filenames
#     filenames2.extend(filenames)

# with open('MEM/Bin Ge.MEF', 'w') as fp:
#     for item in filenames2:
#         # write each item on a new line
#         fp.write("%s\n" % item)
#     print('Done')

# filenames=read_file_lines('MEM/Bin Ge/MSF.MEF')

# FileDict={'A3V1':filenames[:20],
#           'M1V1':filenames[20:40],
#           'R1V1':filenames[40:60],
#           'A3V2':filenames[60:80],
#           'M1V2':filenames[80:100],
#           'R1V2':filenames[100:120]
# }