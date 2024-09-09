import numpy as np
from scipy.special import erf
from scipy.stats import expon

### CMAP Simulation, using the same paradigm outlines in Stairfit paper.

## Chen, M., Lu, Z., Zong, Y., Li, X., & Zhou, P. (2023). A Novel Analysis of Compound Muscle Action Potential Scan: Staircase Function Fitting and StairFit Motor Unit Number Estimation. In IEEE Journal of Biomedical and Health Informatics (Vol. 27, Issue 3, pp. 1579–1587). Institute of Electrical and Electronics Engineers (IEEE). https://doi.org/10.1109/jbhi.2022.3229211

class CMAPSim:

    def __init__(self, NCells, alpha1=200, beta1=25, alpha2=12, beta2=1, alpha3=0, beta3=0.02, length=500, noiseoffset=10, noisedev=5, seed=0):
        """Initialize the simulator with given parameters."""
        self.rng = np.random.default_rng(seed=seed)
        self.NCells = NCells            # Number of Motor Units
        self.alpha1 = alpha1            # Exponential Scale parameter (Mean motor unit amplitude (+ minumum))
        self.beta1 = beta1              # Exponential Location parameter (Minimnum motor unit amplitude)
        self.alpha2 = alpha2            # Activation threshold mean (gaussian)
        self.beta2 = beta2              # Activation threshold deviation (gaussian)
        self.alpha3 = alpha3            # Relative spread lower bound (uniform dist)
        self.beta3 = beta3              # Relative spread upper bound (uniform dist)
        self.length = length            # Lenght of simulation
        self.noiseoffset = noiseoffset  # Additive noise mean
        self.noisedev = noisedev        # Additive noise deviation
        self.x, self.y = self._simulate_amplitudes()

    def _simulate_amplitudes(self):
        """Simulate amplitude responses."""
        Sizes = expon.rvs(scale=self.alpha1, loc=self.beta1, size=self.NCells, random_state=self.rng)
        Thresholds = self.rng.normal(self.alpha2, self.beta2, self.NCells)
        Spreads = self.rng.uniform(self.alpha3, self.beta3, self.NCells)
        Devs = Spreads * Thresholds
        baselinenoise = self.rng.normal(self.noiseoffset, self.noisedev, self.length)
        minstim = min(Thresholds) - 0.5
        maxstim = max(Thresholds) + 0.5

        ModelStims = np.linspace(minstim, maxstim, self.length)
        ModelAmps = [self._calculate_amplitude(Sizes, Thresholds, Devs, stim) for stim in ModelStims]
        ModelAmps = np.array(ModelAmps) + baselinenoise
        return ModelStims, ModelAmps
    
    def _calculate_probabilities(self, Thresholds, Devs, stim):
        """Calculate the sigmoid response probabilities for each unit."""
        return (erf((1/(np.sqrt(2)*Devs))*(stim-Thresholds))+1)/2

    def _calculate_amplitude(self, Sizes, Thresholds, Devs, stim):
        """Determine activation of each unit based on its probability for a given stimulus."""
        PVal = self._calculate_probabilities(Thresholds, Devs, stim)
        Roll = self.rng.uniform(0, 1, len(Sizes))
        Bool = Roll <= PVal
        Amps = Sizes * Bool.astype(int)
        return np.sum(Amps)
    

# Cells = 40
# alpha1 = 0.2
# beta1 = 0.025
# alpha2 = 12
# beta2 = 1
# alpha3 = 0.015
# beta3 = 0.02
# length = 500
# noiseoffset = 0.01
# noisedev = 0.005

# # Execute simulation
# Simulator = CMAPSim(Cells, alpha1, beta1, alpha2, beta2, alpha3, beta3, length, noiseoffset, noisedev)

# import plotly.graph_objects as go

# Fig=go.Figure()

# Fig.add_trace(go.Scatter(x=Simulator.x,y=Simulator.y,mode='markers'))

# Fig.show()