import csv
import numpy as np

def OscopePrintToCSV(csv_file):
    waveform_dict = {}
    line_keys = []
    line0_key = ''
    line1_key = ''
    with open(csv_file,"r") as f:
        for j,line in enumerate(csv.reader(f)):
            if j == 0: continue
            if j == 1:
                for i,entry in enumerate(line):
                    if i>0:
                        waveform_dict["ch"+str(i)] = {"second": []}
                        waveform_dict["ch"+str(i)][entry] = []
            else:
                for i,entry in enumerate(line):
                    if i == 0:
                        for ch in waveform_dict:
                            waveform_dict[ch]["second"].append(float(line[0]))
                    else:
                        waveform_dict["ch"+str(i)]["Volt"].append(float(line[i]))
    for ch in waveform_dict:
        for key in waveform_dict[ch]:
            waveform_dict[ch][key] = np.array(waveform_dict[ch][key])
    return waveform_dict
