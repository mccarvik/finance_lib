import sys, pdb
sys.path.append("/home/ubuntu/workspace/finance_lib")

import numpy as np
import pandas as pd
import datetime as dt

from utils.fi_funcs import *
from dx.frame import get_year_deltas

# http://www.financialexamhelp123.com/par-curve-spot-curve-and-forward-curve/
# zero rate (aka spot rate) - rate for a given cash flow at a give point in time
# fwd rate - rate from one period in time in the future to a second period of time in the future
# par rate - rate at a given maturity matching the YTM of a coupon paying bond at that maturity

class ZeroCurve(object):
    """
    ZeroCurve object - handles basic nominal discounting
    Uses the simple interest rate convention.
    """
    def __init__(self, mats, rates):
        ''' Constructor
        Parameters
        ==========
        mats : list of datetimes
            dates of the points on the curve
        rates : list of floats
            rates of the points on the curve
        Return
        ======
        NONE
        '''
        if not len(rates) == len(mats):
            raise ValueError('Zero curve and maturities must be equal length')
        self.mats = mats
        self.rates = rates
    
    def addRate(self, mat, rt):
        self.mats.append(mat)
        self.rates.append(rt)
    
    def getZeroRate(self, mat):
        """
        Get the zero rate at a particular maturity point, must be interior.
        Note that if shortest maturity > 0, we use it for all maturities up to that point as well.
        Note that we assume that the maturity list is sorted
        :param mat: float
        :return: float
        """
        if mat > self.mats[-1]:
            raise ValueError('Maturity longer than longest zero maturity')
        if mat <= self.mats[0]:
            return self.rates[0]
            
        prev_mat = self.mats[0]
        prev_zero = self.rates[0]
        
        # We already tested for the shortest maturity
        for pos in range(1, len(self.mats)):
            if self.mats[pos] == mat:
                return self.rates[pos]
            if self.mats[pos] > mat:
                fac = (mat - prev_mat)/(self.mats[pos] - prev_mat)
                return ((1-fac)*prev_zero) + (fac*self.rates[pos])
            prev_mat = self.mats[pos]
            prev_zero = self.rates[pos]
    
    def getDF(self, trade_dt, mat):
        """
        Return the associated discount factor for a maturity.
        Assumes that the maturity list is sorted.
        :param mat: float
        :return: float
        """
        r = self.getZeroRate(mat)
        mat = get_year_deltas([trade_dt, mat])[-1]
        return calcDiscountFactor(mat, r)
    
    def createFwdCurve(self, trade_dt):
        ''' will make a forward curve from a zero curve
            Assumes that trade_dt will be before first maturity on curve
        '''
        fc = FwdCurve([],[])
        
        # first rate from today to first mat is same as spot rate
        fc.addRate((trade_dt, self.mats[0]), self.rates[0])
        
        prev_mat = self.mats[0]
        prev_rate = self.rates[0]
        
        for pos in range(1, len(self.mats)):
            y_mat = get_year_deltas([trade_dt, prev_mat])[-1]
            x_mat = get_year_deltas([trade_dt, self.mats[pos]])[-1]
            x_spot = self.rates[pos]
            # Forward = [(1 + spot rate for year x)^x / (1 + spot rate for year y)^y] - 1
            fwd_rate = ((1 + x_spot)**x_mat / (1 + prev_rate)**y_mat) - 1
            fc.addRate((prev_mat, self.mats[pos]), fwd_rate)
            prev_mat = self.mats[pos]
            prev_rate = x_spot
        return fc
    
    
class FwdCurve(object):
    """
    Forward Curve object - handles forward curves from one maturity to another
    """
    def __init__(self, mats, rates):
        ''' Constructor
        Parameters
        ==========
        mats : list of datetimes tuples
            tuples will be the start and end date of 
        rates : list of floats
            rates of the points on the curve
        Return
        ======
        NONE
        '''
        if not len(rates) == len(mats):
            raise ValueError('Fwd curve and maturities must be equal length')
        self.mats = mats
        self.rates = rates
    
    def addRate(self, mat, rt):
        self.mats.append(mat)
        self.rates.append(rt)
    
    def createSpotCurve(self, trade_dt):
        ''' will make a spot curve (aka zero curve) from a fwd curve
            Assumes that trade_dt will be before first maturity on curve
        '''
        # TODO
        zc = ZeroCurve([],[])
        
        # first rate from today to first mat is same as spot rate
        zc.addRate(self.mats[0][1], self.rates[0])
        
        prev_mat = self.mats[0][1]
        prev_rate = self.rates[0]
        
        for pos in range(1, len(self.mats)):
            # assumes the next fwd rate picks up where the previous one drops off
            mat_diff = get_year_deltas([self.mats[pos][0], self.mats[pos][1]])[-1]
            prev_date_diff = get_year_deltas([trade_dt, prev_mat])[-1]
            # (1 + r(T*+T))^(T*+T) = (1 + r(T*))^T* * (1 + f(T,T*))^T
            spot_rate = ((1 + prev_rate)**prev_date_diff * (1 + self.rates[pos])**mat_diff)**(1 / (prev_date_diff + mat_diff)) - 1
            zc.addRate(self.mats[pos][1], spot_rate)
            prev_rate = spot_rate
            prev_mat = self.mats[pos][1]
        return zc
    
    
class ParCurve(object):
    """
    Par Curve object - Simply creates a par curve of traded asses
    """
    def __init__(self, insts, pxs, trade_dt):
        ''' Constructor
        Parameters
        ==========
        insts : list of instruments
            will take the ylds on these and pair with their maturities
        pxs : list of floats
            list of market prices associated with each instrument
        Return
        ======
        NONE
        '''
        if not len(insts) == len(pxs):
            raise ValueError('Par curve and maturities must be equal length')
        self.trade_dt = trade_dt
        self.rates = [i.getYield(px, self.trade_dt) for i, px in zip(insts, pxs)]
        self.mats = [i._mat_dt for i in insts]
        self.insts = insts
        self.pxs = pxs
    
    def getParRate(self, mat):
        """
        Get the par rate at a particular maturity point, must be interior.
        Note that if shortest maturity > 0, we use it for all maturities up to that point as well.
        Note that we assume that the maturity list is sorted
        linear interpolation here
        :param mat: float
        :return: float
        """
        prev_mat = self.mats[0]
        prev_par = self.rates[0]
        # We already tested for the shortest maturity
        for pos in range(1, len(self.mats)):
            if self.mats[pos] == mat:
                return self.rates[pos]
            if self.mats[pos] > mat:
                fac = (mat - prev_mat)/(self.mats[pos] - prev_mat)
                return ((1-fac)*prev_par) + (fac*self.rates[pos])
            prev_mat = self.mats[pos]
            prev_par = self.rates[pos]
    