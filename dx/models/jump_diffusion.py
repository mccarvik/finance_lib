from ..frame import *
from .simulation_class import simulation_class


class jump_diffusion(simulation_class):
    ''' Class to generate simulated paths based on
    the Merton (1976) jump diffusion model.
    Attributes
    ==========
    name : string
        name of the object
    mar_env : instance of market_environment
        market environment data for simulation
    corr : boolean
        True if correlated with other model object
    Methods
    =======
    update :
        updates parameters
    generate_paths :
        returns Monte Carlo paths given the market environment
    '''

    def __init__(self, name, mar_env, corr=False):
        super(jump_diffusion, self).__init__(name, mar_env, corr)
        try:
            self.lamb = mar_env.get_constant('lambda')
            self.mu = mar_env.get_constant('mu')
            self.delt = mar_env.get_constant('delta')
        except:
            print('Error parsing market environment.')

    def update(self, pricing_date=None, initial_value=None,
               volatility=None, lamb=None, mu=None, delta=None,
               final_date=None):
        if pricing_date is not None:
            self.pricing_date = pricing_date
            self.time_grid = None
            self.generate_time_grid()
        if initial_value is not None:
            self.initial_value = initial_value
        if volatility is not None:
            self.volatility = volatility
        if lamb is not None:
            self.lamb = lamb
        if mu is not None:
            self.mu = mu
        if delta is not None:
            self.delt = delta
        if final_date is not None:
            self.final_date = final_date
        self.instrument_values = None

    def generate_paths(self, fixed_seed=False, day_count=365.):
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
            sn1 = sn_random_numbers((1, M, I),
                                    fixed_seed=fixed_seed)
        else:
            # if correlated use random number object as provided
            # in market environment
            sn1 = self.random_numbers

        # Standard normally distributed seudo-random numbers
        # for the jump component
        sn2 = sn_random_numbers((1, M, I),
                                fixed_seed=fixed_seed)

        forward_rates = self.discount_curve.get_forward_rates(
            self.time_grid, self.paths, dtobjects=True)[1]

        
        # rj --> drift correction for the riskless rate so jumps maintain risk neutrality
        rj = self.lamb * (np.exp(self.mu + 0.5 * self.delt ** 2) - 1)
        
        for t in range(1, len(self.time_grid)):
            # select the right time slice from the relevant
            # random number set
            if self.correlated is False:
                ran = sn1[t]
            else:
                # only with correlation in portfolio context
                # A list of random numbers is generated for each member
                # Cholesky correlation matrix then used to ensure the random numbers are appropriately correlated
                ran = np.dot(self.cholesky_matrix, sn1[:, t, :])
                ran = ran[self.rn_set]
            
            # difference between two dates as year fraction
            dt = (self.time_grid[t] - self.time_grid[t - 1]).days / day_count
            
            # Poisson distributed pseudo-random numbers for jump component
            # will determine whether a jump occurs or not given lambda
            poi = np.random.poisson(self.lamb * dt, I)
            
            # Interpolated rate for this step
            rt = (forward_rates[t - 1] + forward_rates[t]) / 2
            
            # next = prev * (e^(r - rj - 0.5 * sigma^2 * dt + sigma * sqrt(dt) * rand) + possible jump)
            # (e^(mu + delta*rand) - 1) * poi --> will add jump compoenent if there is a jump, poi will be 0 if not
            paths[t] = paths[t - 1] * (np.exp((rt - rj - 0.5 * self.volatility ** 2) * dt + 
                        self.volatility * np.sqrt(dt) * ran) + (np.exp(self.mu + self.delt * sn2[t]) - 1) * poi)
        self.instrument_values = paths