import numpy as np

#Fit functions
def gauss(x, H, A, x0, sigma):
    '''
    Gaussian function used in fitting.
    inputs:
        x [array]
        Data to fit gaussian to.
        H [float]
        Constant offset added to gaussian.
        A [float]
        Amplitude term for gaussian.
        x0 [float]
        Mean of gaussian.
        sigma [float]
        Spread of gaussian.
        returns H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    '''
    return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

