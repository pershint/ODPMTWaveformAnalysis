#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt

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
    wavefile = sys.argv[1]
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
   
        ######## BEGIN WAVEFORM PLOTTING AND PULSE FITTING ########
        #Show the waveform's baseline estimation, and pulses found
        have_pulse = False
        for pulse in pulses:
            if not have_pulse:
                plt.vlines(waveform['second'][pulse['min_time_sample']]*1E9,ymin=bl_mean, ymax =pulse['peak_amplitude'], color='purple', linewidth=2,label='Pulses')
                have_pulse = True
            else:
                plt.vlines(waveform['second'][pulse['min_time_sample']]*1E9,ymin=bl_mean, ymax =pulse['peak_amplitude'], color='purple', linewidth=2)
            plt.vlines(waveform['second'][pulse['max_time_sample']]*1E9,ymin=bl_mean, ymax =pulse['peak_amplitude'], color='purple', linewidth=2)
            plt.hlines(pulse['peak_amplitude'], xmin=waveform['second'][pulse['min_time_sample']]*1E9,xmax=waveform['second'][pulse['max_time_sample']]*1E9, color='purple', linewidth=2)
            plt.hlines(bl_mean, xmin=waveform['second'][pulse['min_time_sample']]*1E9,xmax=waveform['second'][pulse['max_time_sample']]*1E9, color='purple', linewidth=2)
        plt.plot(waveform['second']*1E9,waveform['Volt'],label='Data')
        bl_min = waveform['second'][BL_RANGE_NSAMP[0]]*1E9
        bl_max = waveform['second'][BL_RANGE_NSAMP[1]]*1E9
        #Show baseline estimation
        plt.hlines(bl_mean,xmin=bl_min, xmax = bl_max,color='black', label = 'Baseline mean', linewidth=2)
        plt.hlines(bl_mean + bl_sigma, xmin=bl_min, xmax = bl_max,color='red',alpha=0.4, label = 'Baseline sigma',linewidth=2)
        plt.hlines(bl_mean -bl_sigma,  xmin=bl_min, xmax = bl_max,color='red',alpha=0.4,linewidth=2)

        #Initialize pulse fitter
        myPulseFitter = pf.PulseFitter()
        for j,pulse in enumerate(pulses):
            #Get pulse region quantities needed for fitting
            time_min = pulse["min_time_sample"]
            time_max = pulse["max_time_sample"]
            poi_volts = waveform['Volt'][time_min:time_max]
            poi_time = waveform['second'][time_min:time_max]*1E9

            if DEBUG:
                print("PULSE NUMBER: " + str(j))
                print("PULSE PEAK AMPLITUDE: %f"%(pulse['peak_amplitude']))
                print("PULSE PEAK AMPLITUDE TIME: %f ns"%(waveform["second"][pulse['peak_amplitude_sample']]*1E9))
                print("TIME MIN: %i"%(pulse["min_time_sample"]))
                print("TIME MAX: %i"%(pulse["max_time_sample"]))
                print("VOLTAGE VALUES FOR PULSE: "+str(poi_volts))
                print("TIME VALUES FOR PULSE: "+str(poi_time))

            #n = len(poi_volts)
            #mean = sum(poi_volts*poi_time)/n
            #sigma = stats.tstd(poi_volts)
            #mean = sum(x * y) / sum(y) 
            #sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
            #initial_guess_params=[min(y), 2*max(y), mean, sigma]
            mean = pulse['peak_time']*1E9
            sigma = (waveform['second'][time_max]*1E9 - waveform['second'][time_min]*1E9)/2.0

            initial_guess_params=[bl_mean, 2*min(poi_volts), mean, sigma]
            print("initial_guess_params are: " + str(initial_guess_params) )
            popt, pcov, fit_good = myPulseFitter.gauss_fit(poi_time,poi_volts,initial_guess_params)
            if fit_good:
                H, A, x0, sigma = popt[0], popt[1], popt[2], popt[3]
                FWHM = 2.35482 * sigma

                if DEBUG:
                    print('The offset of the gaussian baseline is', H)
                    print('The center of the gaussian fit is', x0)
                    print('The sigma of the gaussian fit is', sigma)
                    print('The maximum intensity of the gaussian fit is', H + A)
                    print('The Amplitude of the gaussian fit is', A)
                    print('The FWHM of the gaussian fit is', FWHM)
                gaus_label = "Fit: Amplitude = " + str(A) + "V, Peak centre = " + str(x0) + "ns."
                #plt.plot(poi_time, fu.gauss(np.array(poi_time), H, A, x0, sigma), '--r', label=gaus_label)
            else:
                print("Failed fit for pulse %i! Skipping..."%(j))


        plt.xlabel("Time (ns)")
        plt.ylabel("Voltage (V)")
        plt.title("Waveform from OD PMT 902 ")#\n (Signal to oscilloscope with 1 MOhm impedance)")
        plt.legend(loc=4)
        plt.show()
    
        ######## END WAVEFORM PLOTTING AND PULSE FITTING ########

        ######## BEGIN ATTENUATION AND CABLE LENGTH CALCULATIONS BASED ON FITS ########
        if len(pulses) < 2:
            print("Not enough pulses in channel to estimate cable length.  Continuing.")
            continue
        main_pulse = pulses[0]
        first_reflection = pulses[1]
        
        #Calculate cable length
        #CONSTANTS
        c = 0.297 #m/ns
        v_p = 1.46 #ns/foot of signal cable
        meters_per_foot = 0.3048
        ReflectionTravelTimeNs = first_reflection["peak_time"]*1E9 - main_pulse["peak_time"]*1E9
        print("TIME DIFFERENCE IN MAIN PEAK AND FIRST REF (ns): %f"%(ReflectionTravelTimeNs))
        
        CableLengthEstimate = (ReflectionTravelTimeNs/v_p)*meters_per_foot
        print("2 * (CABLE LENGTH ESTIMATE + 2 m LEAD CABLE): %f"%(CableLengthEstimate))
        print("CABLE LENGTH ESTIMATE: %f"%((CableLengthEstimate-4)/2.0))

        #Estimate attenuation
        MainPulseInt = main_pulse['integral']
        FirstReflectionInt = first_reflection['integral']
        print("FIRST REFLECTION INTEGRAL / MAIN PULSE INTEGRAL: %f / %f"%(FirstReflectionInt,MainPulseInt))
        print("LOSS IN 2 * (CABLE LENGTH ESTIMATE + 2 m LEAD CABLE): %f"%(FirstReflectionInt/MainPulseInt))

        MainPulsePeak = main_pulse['peak_amplitude']
        FirstReflectionPeak = first_reflection['peak_amplitude']
        print("FIRST REFLECTION AMPLITUDE / MAIN PULSE AMPLITUDE: %f / %f"%(FirstReflectionPeak,MainPulsePeak))
        print("AMPLITUDE REDUCTION IN 2 * (CABLE LENGTH ESTIMATE + 2 m LEAD CABLE): %f"%(FirstReflectionPeak/MainPulsePeak))
