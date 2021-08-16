#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context("poster")
sns.set_style("darkgrid")

import lib.PulseFinder as pu
import lib.PulseFitter as pf
import lib.Functions as fu
import lib.BaselineFinder as bf
import lib.ProcessingUtils as prut



if __name__ == '__main__':
    #BEGIN CONFIGURABLES
    PULSE_THRESHOLD = 4
    #ADDEDGE_NSAMPS = 30 #good for reflection scope traces
    #ADDEDGE_NSAMPS = 0 #good for zoomed scope traces
    ADDEDGE_NSAMPS = 10 #Good for reflection scope traces
    BL_RANGE_NSAMP = [0, 100] #good for reflections cope traces
    #BL_RANGE_NSAMP = [0,200] #good for zoomed pulses
    DEBUG = False
    #END CONFIGURABLES

    #Load waveform from Oscilloscope file 
    wavefiles = sys.argv[1:len(sys.argv)-1]
    pulse_times = []
    for wavefile in wavefiles:
        waveforms = prut.OscopePrintToCSV(wavefile)

        #Initialize PulseFinder
        myPulseFinder = pu.PulseFinder()
        myPulseFinder.SetPulseThreshold(PULSE_THRESHOLD) #nsigma outside baseline to define a pulse
        myPulseFinder.SetEdgeSamples(ADDEDGE_NSAMPS)

        myBaselineFinder = bf.BaselineFinder()

        for ch in waveforms:
            print("ANALYZING CHANNEL %s NOW"%(ch))
            waveform = waveforms[ch]
            bl_mean, bl_sigma = myBaselineFinder.EstimateSimpleBaseline(waveform['Volt'],BL_RANGE_NSAMP)
            pulses = myPulseFinder.FindPulsesSimpleBaseline(waveform['second'],waveform['Volt'],bl_mean,bl_sigma)
   
            for pulse in pulses:
                pulse_times.append(pulse["peak_time"]*1E9)
    plt.hist(pulse_times,bins=40,range=(-300,300), color='orange')
    plt.xlabel("Pulse peak time (ns)")
    plt.ylabel("Number of pulses")
    plt.title("Pulse time distribution for PMTs in OD \n (PMTs 912, 914, 916, and 902)")
    plt.show()
