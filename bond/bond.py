import sys, pdb
sys.path.append("/home/ubuntu/workspace/finance_lib")
from dateutil.relativedelta import relativedelta

import datetime as dt


class Bond():
    """This class will hold all the variables associated with a fixed rate bond"""
    
    def __init__(self, mat_dt=dt.datetime.now()+dt.timedelta(days=365), par=100):
        ''' Constructor
        Parameters
        ==========
        mat_dt : str
            maturity date of the bond
        par : float
            par value of the bond, DEFAULT = 100

        Return
        ======
        NONE
        '''
        self._mat_dt = mat_dt
        self._par = par
