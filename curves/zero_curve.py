import sys, pdb
sys.path.append("/home/ubuntu/workspace/finance_lib")

import numpy as np
import pandas as pd
import datetime as dt


class ZeroCurve(object):
    """
    ZeroCurve object - handles basic nominal discounting
    Uses the simple interest rate convention.
    """
    def __init__(self, mats, rates):
        """
        Initialise the ZeroCurve
        :param ZC: list
        :param mats: list
        """
        if not len(rates) == len(mats):
            raise ValueError('Zero curve and maturities must be equal length')
        self.mats = mats
        self.rates = rates
    
    def GetZeroRate(self, mat):
        """
        Get the zero rate at a particular maturity point, must be interior.
        Note that if shortest maturity > 0, we use it for all maturities up to that point as well.
        Note that we assume that the maturity list is sorted
        :param mat: float
        :return: float
        """
        if mat < 0:
            raise ValueError('Negative maturity - fail')
        if mat > self.mats[-1]:
            raise ValueError('Maturity longer than longest zero maturity')
        if mat <= self.mats[0]:
            return self.mats[0]
            
        prev_mat = self.mats[0]
        prev_zero = self.rates[0]
        
        # We already tested for the shortest maturity
        for pos in range(1, len(self.mats)):
            if self.mats[pos] == mat:
                return self.rates[pos]
            if self.mats[pos] > mat:
                fac = (mat - prev_mat)/(self.mats[pos] - prev_mat)
                return ((1-fac)*prev_zero) + (fac*self.rates)
            prev_mat = self.mats[pos]
            prev_zero = self.rates[pos]
        