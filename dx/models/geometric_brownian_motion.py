from ..frame import *
from .simulation_class import simulation_class


class geometric_brownian_motion(simulation_class):
    ''' Class to generate simulated paths based on
    the Black-Scholes-Merton geometric Brownian motion model.
    Attributes
    ==========
    name : string
        name of the object
    mar_env : instance of market_environment
        market environment data for simulation
    corr : boolean
        True if correlated with other model simulation object
    Methods
    =======
    update :
        updates parameters
    generate_paths :
        returns Monte Carlo paths given the market environment
    '''

    def __init__(self, name, mar_env, corr=False):
        super(geometric_brownian_motion, self).__init__(name, mar_env, corr)

    def update(self, pricing_date=None, initial_value=None, volatility=None, final_date=None):
        ''' Updates model parameters. '''
        if pricing_date is not None:
            self.pricing_date = pricing_date
            self.time_grid = None
            self.generate_time_grid()
        if initial_value is not None:
            self.initial_value = initial_value
        if volatility is not None:
            self.volatility = volatility
        if final_date is not None:
            self.final_date = final_date
        self.instrument_values = None

    def generate_paths(self, fixed_seed=False, day_count=365.):
        ''' Generates Monte Carlo paths for the model. '''
        if self.time_grid is None:
            self.generate_time_grid()
            # method from generic model simulation class
        # number of dates for time grid
        M = len(self.time_grid)
        # number of paths
        I = self.paths
        # array initialization for path simulation
        paths = np.zeros((M, I))
        # initialize first date with initial_value
        paths[0] = self.initial_value
        if self.correlated is False:
            # if not correlated generate random numbers
            rand = sn_random_numbers((1, M, I), fixed_seed=fixed_seed)
        else:
            # if correlated use random number object as provided
            # in market environment
            rand = self.random_numbers

        # forward rates for drift of process
        forward_rates = self.discount_curve.get_forward_rates(self.time_grid, self.paths, dtobjects=True)[1]

        for t in range(1, len(self.time_grid)):
            # select the right time slice from the relevant
            # random number set
            if self.correlated is False:
                ran = rand[t]
            else:
                # A list of random numbers is generated for each member
                # Cholesky correlation matrix then used to ensure the random numbers are appropriately correlated
                # A matrix * the cholesky correlation matrix creates an array of correlated values
                ran = np.dot(self.cholesky_matrix, rand[:, t, :])
                ran = ran[self.rn_set]
            dt = (self.time_grid[t] - self.time_grid[t - 1]).days / day_count
            
            # rt = the drift factor
            # difference between two dates as year fraction
            rt = (forward_rates[t - 1] + forward_rates[t]) / 2
            
            # No rate volatility - true Brownian motion
            # paths[t] = paths[t - 1] + rt * dt + self.volatility * np.sqrt(dt) * ran
            
            # With rate volatility
            paths[t] = paths[t - 1] * np.exp((rt - 0.5 * self.volatility ** 2) * dt + self.volatility * np.sqrt(dt) * ran)
            # generate simulated values for the respective date
        self.instrument_values = paths