import numpy as np

class PulseFinder(object):
    def __init__(self):
        self.nsigma = None
        self.edge_addnsamps = None

    def SetPulseThreshold(self, nsigma):
        self.nsigma = nsigma

    def SetEdgeSamples(self, edge_addnsamps):
        self.edge_addnsamps = edge_addnsamps

    def FindPulses_SimpleBaseline(self, wx,wy, bl_mean, bl_sigma):
        '''
        Comments
        '''
        pulses = []
        pulse = {'peak_time': -9999,'min_time_sample': -9999, 'max_time_sample': -9999, 'peak_amplitude': -9999, 'pulse_integral': 0}
        in_pulse = False
        bl_counter = 0
        #TODO:  We can make this faster
        #  - Do a np.where() to find where the waveform goes outside baseline fluctuation
        #  - adjust for logic to look across those samples and define waveforms
        #    This way, you're not looping over so many values in the for loop
        for j,raw_sample in enumerate(wy):
            sample = raw_sample - bl_mean
            if np.abs(sample) > bl_sigma*self.nsigma and not in_pulse:
                bl_counter = 0
                in_pulse = True
                print("IN PULSE")
                pulse['peak_amplitude'] = sample
                pulse['peak_amplitude_sample'] = j
                pulse['min_time_sample'] = j - self.edge_addnsamps
                if pulse['min_time_sample'] < 0: 
                    pulse['min_time_sample'] = 0
            elif np.abs(sample) > bl_sigma*self.nsigma: #Execute if still in pulse
                bl_counter = 0
                if np.abs(sample) > np.abs(pulse['peak_amplitude']):
                    pulse['peak_amplitude'] = sample
                    pulse['peak_time'] = wy[j]
                pulse['pulse_integral']+=sample
            elif in_pulse: #no longer in a pulse
                if bl_counter < 5:
                    bl_counter+=1
                    continue
                else:
                    print("OUT OF PULSE")
                    bl_counter = 0
                    in_pulse = False
                    pulse['max_time_sample'] = j + self.edge_addnsamps
                    pulses.append(pulse)
                    pulse = {'peak_time': -9999,'min_time_sample': -9999, 'max_time_sample': -9999, 'peak_amplitude': -9999, 'pulse_integral': 0}
        return pulses
