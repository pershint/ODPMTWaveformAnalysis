#!/usr/bin/env python
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
import lib.PulseFinder as pu

from scipy.optimize import curve_fit
from scipy import stats
from scipy import asarray as ar,exp

def OscopePrintToCSV(csv_file):
    waveform_dict = {}
    line0_key = ''
    line1_key = ''
    with open(csv_file,"r") as f:
        for j,line in enumerate(csv.reader(f)):
            if j == 0: continue
            if j == 1:
                line0_key = line[0]
                line1_key = line[1]
                waveform_dict[line[0]] = []
                waveform_dict[line[1]] = []
            else:
                waveform_dict[line0_key].append(float(line[0]))
                waveform_dict[line1_key].append(float(line[1]))
    for entry in waveform_dict:
        waveform_dict[entry] = np.array(waveform_dict[entry])
    return waveform_dict

def EstimateSimpleBaseline(waveform, bl_range):
    bl_samples = waveform[bl_range[0]:bl_range[1]]
    bl_mean = np.average(bl_samples)
    bl_sigma = np.std(bl_samples)
    return bl_mean, bl_sigma

if __name__ == '__main__':
    myPulseFinder = pu.PulseFinder()
    myPulseFinder.SetPulseThreshold(15) #nsigma outside baseline to define a pulse
    myPulseFinder.SetEdgeSamples(6)
    BL_RANGE_NSAMP = [0, 60]
    #print("Let's analyze a waveform")
    #print("usage: main.py [waveform_filename]")
    wavefile = sys.argv[1]
    waveform = OscopePrintToCSV(wavefile)
    mu, sigma = EstimateSimpleBaseline(waveform['Volt'],BL_RANGE_NSAMP)
    pulses = myPulseFinder.FindPulses_SimpleBaseline(waveform['second'],waveform['Volt'],mu,sigma)
    have_pulse = False
    for pulse in pulses:
        if not have_pulse:
            plt.vlines(waveform['second'][pulse['min_time_sample']]*1E9,ymin=0, ymax =pulse['peak_amplitude'], color='purple', linewidth=2,label='Pulses')
        else:
            plt.vlines(waveform['second'][pulse['min_time_sample']]*1E9,ymin=0, ymax =pulse['peak_amplitude'], color='purple', linewidth=2)
        plt.vlines(waveform['second'][pulse['max_time_sample']]*1E9,ymin=0, ymax =pulse['peak_amplitude'], color='purple', linewidth=2)
        plt.hlines(pulse['peak_amplitude'], xmin=waveform['second'][pulse['min_time_sample']]*1E9,xmax=waveform['second'][pulse['max_time_sample']]*1E9, color='purple', linewidth=2)
        plt.hlines(0, xmin=waveform['second'][pulse['min_time_sample']]*1E9,xmax=waveform['second'][pulse['max_time_sample']]*1E9, color='purple', linewidth=2)
    plt.plot(waveform['second']*1E9,waveform['Volt']- mu,label='Data (BL-Subtracted)')
    bl_min = waveform['second'][BL_RANGE_NSAMP[0]]*1E9
    bl_max = waveform['second'][BL_RANGE_NSAMP[1]]*1E9
    #plt.hlines(mu,xmin=bl_min, xmax = bl_max,color='black', label = 'Baseline mean', linewidth=2)
    plt.hlines(sigma, xmin=bl_min, xmax = bl_max,color='red',alpha=0.4, label = 'Baseline sigma',linewidth=2)
    plt.hlines(-sigma,  xmin=bl_min, xmax = bl_max,color='red',alpha=0.4,linewidth=2)
    
    plt.xlabel("Time (ns)")
    plt.ylabel("Voltage (V)")
    plt.title("Waveform from OD PMT 902 ")#\n (Signal to oscilloscope with 1 MOhm impedance)")
    for j,pulse in enumerate(pulses):
        print("PULSE NUMBER: " + str(j))
        print("PULSE PEAK AMPLITUDE: %f"%(pulse['peak_amplitude']))
        print("PULSE PEAK AMPLITUDE TIME: %f ns"%(waveform["second"][pulse['peak_amplitude_sample']]*1E9))
        print("TIME MIN: %i"%(pulse["min_time_sample"]))
        print("TIME MAX: %i"%(pulse["max_time_sample"]))
        time_min = pulse["min_time_sample"]
        time_max = pulse["max_time_sample"]
        poi_volts = waveform['Volt'][time_min:time_max]
        poi_time = waveform['second'][time_min:time_max]*1E9
        print("VOLTAGE VALUES FOR PULSE: "+str(poi_volts))
        print("TIME VALUES FOR PULSE: "+str(poi_time))

        n = len(poi_volts)
        #mean = sum(poi_volts*poi_time)/n
        mean = pulse['peak_amplitude']
        sigma = stats.tstd(poi_volts)

    
        def gauss(x, H, A, x0, sigma):
            return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
        
        def gauss_fit(x, y):
            mean = sum(x * y) / sum(y) 
            sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
            popt, pcov = curve_fit(gauss, x, y, p0=[min(y), 2*max(y), mean, sigma])
            return popt
    
        volt_fit = gauss_fit(poi_time,poi_volts)

        H, A, x0, sigma = gauss_fit(poi_time,poi_volts)
        FWHM = 2.35482 * sigma

        print('The offset of the gaussian baseline is', H)
        print('The center of the gaussian fit is', x0)
        print('The sigma of the gaussian fit is', sigma)
        print('The maximum intensity of the gaussian fit is', H + A)
        print('The Amplitude of the gaussian fit is', A)
        print('The FWHM of the gaussian fit is', FWHM)
        mean  = format(mean, '.5f')
        x0 = format(x0, '.5f')
        gaus_label = "Fit: Max voltage = " + str(mean) + "V, Peak centre = " + str(x0) + "ns."
        plt.plot(poi_time, gauss(poi_time, *gauss_fit(poi_time, poi_volts))-mu, '--r', label=gaus_label)



    plt.legend()
    #plt.savefig()
    print(wavefile)
    plt.show()