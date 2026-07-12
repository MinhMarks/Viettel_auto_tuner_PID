import numpy as np

class FuzzyPID:
    """
    A lightweight Mamdani Fuzzy Inference System for tuning PID gains dynamically.
    Outputs Delta Kp and Delta Kd based on Error and Change in Error.
    """
    def __init__(self, kp_scale=10.0, kd_scale=5.0):
        self.kp_scale = kp_scale
        self.kd_scale = kd_scale
        
    def trimf(self, x, abc):
        a, b, c = abc
        if x <= a or x >= c: return 0.0
        if a < x <= b: return (x - a) / (b - a)
        if b < x < c: return (c - x) / (c - b)
        return 0.0
        
    def compute_memberships(self, val, scale):
        # Scale input to roughly [-1, 1] range for membership evaluation
        val = np.clip(val / scale, -1, 1)
        sets = {
            'NB': self.trimf(val, [-2.0, -1.0, -0.5]),
            'NM': self.trimf(val, [-1.0, -0.5, 0.0]),
            'ZE': self.trimf(val, [-0.5, 0.0, 0.5]),
            'PM': self.trimf(val, [0.0, 0.5, 1.0]),
            'PB': self.trimf(val, [0.5, 1.0, 2.0])
        }
        return sets
        
    def compute_delta(self, e, ec, e_scale=1.5, ec_scale=5.0):
        """
        e: current error
        ec: derivative of error (rate of change)
        Returns: dKp, dKd
        """
        m_e = self.compute_memberships(e, e_scale)
        m_ec = self.compute_memberships(ec, ec_scale)
        
        # Rule Base for dKp
        # rows: Error (NB, NM, ZE, PM, PB)
        # cols: dError (NB, NM, ZE, PM, PB)
        rules_kp = [
            ['PB', 'PB', 'PM', 'PM', 'ZE'],
            ['PB', 'PB', 'PM', 'PM', 'ZE'],
            ['PM', 'PM', 'ZE', 'NM', 'NM'],
            ['PM', 'PM', 'ZE', 'NM', 'NM'],
            ['ZE', 'ZE', 'NM', 'NB', 'NB']
        ]
        
        # Rule Base for dKd
        rules_kd = [
            ['PM', 'PM', 'ZE', 'NM', 'NB'],
            ['PM', 'PM', 'ZE', 'NM', 'NB'],
            ['ZE', 'ZE', 'ZE', 'NM', 'NM'],
            ['PM', 'PM', 'ZE', 'NM', 'NB'],
            ['PB', 'PB', 'ZE', 'NM', 'NB']
        ]
        
        # Output centroids for defuzzification
        out_map = {'NB': -1.0, 'NM': -0.5, 'ZE': 0.0, 'PM': 0.5, 'PB': 1.0}
        
        num_kp = 0.0
        num_kd = 0.0
        den = 0.0
        
        states = ['NB', 'NM', 'ZE', 'PM', 'PB']
        for i, st_e in enumerate(states):
            for j, st_ec in enumerate(states):
                weight = min(m_e[st_e], m_ec[st_ec]) # AND operator
                if weight > 0:
                    num_kp += weight * out_map[rules_kp[i][j]]
                    num_kd += weight * out_map[rules_kd[i][j]]
                    den += weight
                    
        if den == 0:
            return 0.0, 0.0
            
        dkp_norm = num_kp / den
        dkd_norm = num_kd / den
        
        # Scale back to actual gain units
        dkp = dkp_norm * self.kp_scale
        dkd = dkd_norm * self.kd_scale
        
        return dkp, dkd
