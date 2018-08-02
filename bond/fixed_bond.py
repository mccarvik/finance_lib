import sys, pdb
sys.path.append("/home/ubuntu/workspace/finance_lib")
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
import datetime as dt

from utils.fi_funcs import *
from dx.frame import deterministic_short_rate, get_year_deltas
from bond import Bond


class FixedRateBond(Bond):
    """This class will hold all the variables associated with a fixed rate bond"""
    
    def __init__(self, mat_dt=dt.datetime.now()+dt.timedelta(days=365), first_pay_dt=None, freq=0.5, cpn=0, dcc="ACT/ACT", 
                 par=100, issue_dt=dt.datetime.today()):
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
        self._pay_freq = freq
        self._issue_dt = issue_dt
        
        if first_pay_dt:
            self._first_pay_dt = datetime.date(int(first_pay_dt[0:4]), int(first_pay_dt[5:7]), int(first_pay_dt[8:10]))
            self._cash_flows = createCashFlows(self._first_pay_dt, self._pay_freq, self._mat_dt, self._cpn, self._par)
            self._cash_flows.insert(0, (self._first_pay_dt, self._cpn * self._par * freq))
        else:
            self._cash_flows = createCashFlows(self._issue_dt, self._pay_freq, self._mat_dt, self._cpn, self._par)
    
    def getPrice(self, yld, trade_dt=dt.datetime.today(), cont=False):
        ''' calculates the price of the bond, given yield and trade date
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
        return cumPresentValue(trade_dt, yld, self._cash_flows, self._pay_freq, cont=False)


if __name__ == '__main__':
    bond = FixedRateBond(mat_dt=dt.datetime(2024, 1, 1), freq=1, cpn=5, issue_dt=dt.datetime(2014, 1, 1))
    # bond = FixedRateBond(trade_dt=dt.datetime(2014, 2, 15), mat_dt=dt.datetime(2024, 2, 15), freq=0.5, cpn=5, ytm=4.8)
    print(bond.getPrice(0.05, trade_dt=dt.datetime(2014, 1, 1)))