import numpy as np

class BaselineFinder(object):
    def __init__(self):
        print("INITIALIZING BASELINE FINDER")

    def EstimateSimpleBaseline(self,waveform, bl_range):
        '''
        For a given waveform, calculate the mean and standard deviation
        of the data points in that region.

        Inputs:
            waveform [array]
            Full waveform of interest.

            bl_range [array]
            Two-element array, where the first value is the minimum index number and
            the second value is the maximum index number of the waveform of the range
            to calculate baseline over.
        
        Outputs:
            bl_mean [float]
            Mean of the samples in range specified.
            bl_sigma [float]
            Standard deviation of samples in range specified.
        '''
        bl_samples = waveform[bl_range[0]:bl_range[1]]
        bl_mean = np.average(bl_samples)
        bl_sigma = np.std(bl_samples)
        return bl_mean, bl_sigma
