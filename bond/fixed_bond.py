import sys, pdb
sys.path.append("/home/ubuntu/workspace/finance_lib")
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import datetime as dt

from utils.fi_funcs import *
from dx.frame import deterministic_short_rate, get_year_deltas
from bond.bond import Bond
from curves.curves import ZeroCurve


class FixedRateBond(Bond):
    """This class will hold all the variables associated with a fixed rate bond"""
    
    def __init__(self, mat_dt=dt.datetime.now()+dt.timedelta(days=365), first_pay_dt=None, freq=0.5, cpn=0, dcc="ACT/ACT", par=100, issue_dt=dt.datetime.today()):
        ''' Constructor
        Parameters
        ==========
        mat_dt : str
            maturity date of the bond
        first_pay_dt : str
            first payment date, need this as some bonds have a short stub period before first payment
            instead of a full accrual period, DEFAULT = None
        issue_dt : str
            Simply used as starting point for cash flows, DEFAULT = today
        freq : float
            payment frequency of the bond, expressed in fractional terms of 1 year, ex: 0.5 = 6 months
            DEFAULT = 0.5
        cpn : float
            coupon rate of the bond, expressed in percent terms not dollar amount, DEFAULT = 0
            NOTE - will come in as percent value and divided by 100, ex 2% / 100 = 0.02
        dcc : str
            day count convention, DEFAULT = "ACT/ACT"
        par : float
            par value of the bond, DEFAULT = 100
        
        Return
        ======
        NONE
        '''
        super().__init__(mat_dt, par)
        self._dcc = dcc or "ACT/ACT"
        self._cpn = cpn / 100 if cpn else 0
        self._freq = freq
        self._issue_dt = issue_dt
        
        if first_pay_dt:
            self._first_pay_dt = datetime.date(int(first_pay_dt[0:4]), int(first_pay_dt[5:7]), int(first_pay_dt[8:10]))
            self._cash_flows = createCashFlows(self._first_pay_dt, self._freq, self._mat_dt, self._cpn, self._par)
            self._cash_flows.insert(0, (self._first_pay_dt, self._cpn * self._par * freq))
        else:
            self._cash_flows = createCashFlows(self._issue_dt, self._freq, self._mat_dt, self._cpn, self._par)
    
    def getPrice(self, yld, trade_dt=dt.datetime.today(), cont=False):
        ''' calculates the price of the bond, given yield and trade date
            Will be the dirty price of the bond
        Parameters
        ==========
        trade_dt : date
            trade date
        yld : float
            current flat discount rate 
        cont : bool
            if the compounding is continuous or not
        
        Return
        ======
        cum_pv : float
            price of the bond
        '''
        return cumPresentValue(trade_dt, yld, self._cash_flows, self._freq, cont=False)

    def getYield(self, px, trade_dt=dt.datetime.today()):
        ''' Will calculate YTM from pv
        Parameters
        ==========
        px : float
            price of bond
        trade_dt : date
            trade date
        
        Return
        ======
        tuple
            pair of pv and ytm
        '''
        return calcYieldToDate(px, self._par, self._mat_dt, self._cpn, freq=self._freq, start_date=trade_dt)
    
    def calcDurationModified(self, px, trade_dt=dt.datetime.today()):
        # Units: for every 1% movement in interest rates, bond in price by 2.621%.
        ytm = self.getYield(px, trade_dt)
        dur = 0
        for cf in self._cash_flows:
            t = (cf[0] - trade_dt).days / 365
            # get present valye of cash flow * how many years away it is
            d_temp =  t * (calcPV(cf[1], (ytm * self._freq), (t / self._freq)))
            # divide by Bond price
            dur += (d_temp / px)
        return dur
    
    def calcDurationMacauley(self, px, trade_dt=dt.datetime.today()):
        # Weighted average # of yrs until the pv of the bond's cash flows equals amount paid for the bond
        ytm = self.getYield(px, trade_dt)
        dur = 0
        for cf in self._cash_flows:
            t = (cf[0] - trade_dt).days / 365
            # get present valye of cash flow * how many years away it is
            d_temp = t * (calcPVContinuous(cf[1], (ytm * self._freq), (t / self._freq)))
            # divide by Bond price
            dur += (d_temp / px)
        return dur
    
    def calcAccruedInterest(self, trade_dt):
        cf = min([c for c in self._cash_flows if c[0] > trade_dt], key = lambda t: t[0])
        t = get_year_deltas([trade_dt, cf[0]])[-1]
        return ((self._freq - t) / self._freq) * cf[1]
    
    def getCleanPrice(self, yld, trade_dt):
        return self.calcPVMidDate(yld, trade_dt) - self.calcAccruedInterest(trade_dt)
    
    def getDirtyPrice(self, yld, trade_dt):
        return self.getCleanPrice(yld, trade_dt) + self.calcAccruedInterest(trade_dt)
        
    def calcPVMidDate(self, yld, trade_dt):
        return cumPresentValue(trade_dt, yld, self._cash_flows, self._freq, cont=False)

    def getPriceFromZeroCurve(self, curve, trade_dt):
        NPV = 0.
        for cf in self._cash_flows:
            NPV += curve.getDF(trade_dt, cf[0]) * cf[1]
        return NPV

    def isBullet(self):
        """ Will return true or false whether this bond is a bullet bond or not"""
        if self._freq == 0:
            return True
        else:
            return False
        
        
if __name__ == '__main__':
    bond = FixedRateBond(mat_dt=dt.datetime(2024, 1, 1), freq=1, cpn=5, issue_dt=dt.datetime(2014, 1, 1))
    # bond = FixedRateBond(trade_dt=dt.datetime(2014, 2, 15), mat_dt=dt.datetime(2024, 2, 15), freq=0.5, cpn=5, ytm=4.8)
    # print(bond.getPrice(0.05, trade_dt=dt.datetime(2014, 1, 1)))
    # print(bond.getDirtyPrice(0.05, trade_dt=dt.datetime(2014, 1, 1)))
    
    # print(bond.getYield(100, trade_dt=dt.datetime(2014, 1, 1)))
    # print(bond.calcDurationModified(100, trade_dt=dt.datetime(2014, 1, 1)))
    # print(bond.calcDurationMacauley(100, trade_dt=dt.datetime(2014, 1, 1)))
    
    curve = ZeroCurve([dt.datetime(2014,1,1), dt.datetime(2015,1,1), dt.datetime(2016,1,1), dt.datetime(2019,1,1), dt.datetime(2024,1,1)], [0, 0.01, 0.02, 0.025, 0.03])
    print(bond.getPriceFromZeroCurve(curve, trade_dt=dt.datetime(2014, 1, 1)))