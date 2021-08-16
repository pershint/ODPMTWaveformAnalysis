import numpy as np
import scipy.optimize as scp
from scipy import stats
from scipy import asarray as ar,exp

from . import Functions as fu

class PulseFitter(object):
    def __init__(self):

        self.minx = None
        self.maxx = None

    def SetFitRange(self, minx, maxx):
        self.minx = minx
        self.maxx = maxx

    
    def gauss_fit(self,x, y, p0):
        if len(p0) != 4:
            print("WARNING: Need four parameters for initial guess of fit.")
            print("(See the gauss function help note.")
        try:
            if self.minx is not None and self.maxx is not None:
                popt, pcov = scp.curve_fit(fu.gauss, x, y, p0=p0, bounds = (self.minx, self.maxx))
            else:
                popt, pcov = scp.curve_fit(fu.gauss, x, y, p0=p0)
            return popt,pcov,True
        except RuntimeError:
            print("Error in fit!  Likely failed.")
            return [-9999], [-9999], False
    
