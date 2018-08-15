import sys
sys.path.append("/home/ubuntu/workspace/finance_lib")
import matplotlib as mpl
mpl.use('Agg')
import datetime, sys, pdb, math
from math import sqrt, pi, log, e
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt

from bond.fixed_bond import FixedRateBond
from curves.curves import ZeroCurve, ParCurve
from utils.fi_funcs import *


def testBootstrap():
    insts = []
    insts.append(FixedRateBond(mat_dt=dt.datetime(2014, 4, 1), freq=0, cpn=0, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2014, 7, 1), freq=0, cpn=0, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2015, 1, 1), freq=0, cpn=0, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2016, 1, 1), freq=0.5, cpn=2, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2017, 1, 1), freq=0.5, cpn=2, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2019, 1, 1), freq=0.5, cpn=2.5, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2024, 1, 1), freq=0.5, cpn=3, issue_dt=dt.datetime(2014, 1, 1)))
    pxs = [99.7, 99.1, 98, 99.5, 99, 99, 100.1]
    pc = ParCurve(insts, pxs, dt.datetime(2014,1,1))
    zc = createZeroCurve(pc, dt.datetime(2014,1,1))
    print(zc.mats)
    print(zc.rates)
    
    insts = []
    insts.append(FixedRateBond(mat_dt=dt.datetime(2014, 7, 1), freq=0, cpn=0, par=101.5, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2015, 1, 1), freq=0, cpn=0, par=104, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2015, 7, 1), freq=0.5, cpn=5, issue_dt=dt.datetime(2014, 1, 1))) 
    pxs = [100, 100, 100]
    pc = ParCurve(insts, pxs, dt.datetime(2014,1,1))
    zc = createZeroCurve(pc, dt.datetime(2014,1,1))
    print(zc.mats)
    print(zc.rates)
    

def testFwdCurveCreate():
    insts = []
    insts.append(FixedRateBond(mat_dt=dt.datetime(2015, 1, 1), freq=1, cpn=9, issue_dt=dt.datetime(2014, 1, 1))) 
    insts.append(FixedRateBond(mat_dt=dt.datetime(2016, 1, 1), freq=1, cpn=9.95, issue_dt=dt.datetime(2014, 1, 1)))
    insts.append(FixedRateBond(mat_dt=dt.datetime(2017, 1, 1), freq=1, cpn=10.85, issue_dt=dt.datetime(2014, 1, 1)))
    pxs = [100, 100, 100]
    pc = ParCurve(insts, pxs, dt.datetime(2014,1,1))
    zc = createZeroCurve(pc, dt.datetime(2014,1,1))
    fc = zc.createFwdCurve(dt.datetime(2014,1,1))
    new_zc = fc.createSpotCurve(dt.datetime(2014,1,1))
    print()
    

if __name__ == '__main__':
    # testBootstrap()
    testFwdCurveCreate()