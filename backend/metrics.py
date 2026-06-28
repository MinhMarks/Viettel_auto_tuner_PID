import numpy as np

def calculate_metrics(time, response, setpoint, control_effort):
    """
    Calculate control system metrics based on time series data.
    
    Args:
        time: List or numpy array of time steps.
        response: List or numpy array of system response values.
        setpoint: Float, the target value.
        control_effort: List or numpy array of control signals (voltages).
        
    Returns:
        dict: A dictionary containing rise_time, settling_time, overshoot, 
              steady_state_error, and control_energy.
    """
    time = np.array(time)
    response = np.array(response)
    control_effort = np.array(control_effort)
    
    metrics = {
        "rise_time": None,
        "settling_time": None,
        "overshoot": 0.0,
        "steady_state_error": 0.0,
        "control_energy": 0.0,
        "itae": 0.0
    }
    
    if len(time) == 0:
        return metrics
        
    if setpoint == 0:
        # Edge case, if setpoint is 0, normal % calculations fail
        steady_state_error = abs(response[-1])
        metrics["steady_state_error"] = steady_state_error
        # Calculate control energy (Integral of squared control effort)
        dt = time[1] - time[0] if len(time) > 1 else 0
        metrics["control_energy"] = np.sum(control_effort**2) * dt
        return metrics

    # 1. Rise Time (10% to 90% of setpoint)
    lower_bound = 0.1 * setpoint
    upper_bound = 0.9 * setpoint
    
    t_10 = None
    t_90 = None
    
    # Assuming step response starting from 0 (or response moving towards setpoint)
    if setpoint > 0:
        idx_10 = np.where(response >= lower_bound)[0]
        idx_90 = np.where(response >= upper_bound)[0]
    else:
        idx_10 = np.where(response <= lower_bound)[0]
        idx_90 = np.where(response <= upper_bound)[0]
        
    if len(idx_10) > 0 and len(idx_90) > 0:
        t_10 = time[idx_10[0]]
        t_90 = time[idx_90[0]]
        if t_90 > t_10:
            metrics["rise_time"] = float(t_90 - t_10)

    # 2. Overshoot (%)
    if setpoint > 0:
        max_val = np.max(response)
        if max_val > setpoint:
            metrics["overshoot"] = float(((max_val - setpoint) / setpoint) * 100)
    else:
        min_val = np.min(response)
        if min_val < setpoint:
            metrics["overshoot"] = float(((min_val - setpoint) / setpoint) * 100)

    # 3. Settling Time (within 5% of setpoint)
    settling_band = 0.05 * abs(setpoint)
    error = np.abs(response - setpoint)
    
    # Find points outside the 5% band
    outside_band_idx = np.where(error > settling_band)[0]
    
    if len(outside_band_idx) > 0:
        # Settling time is the time of the last point outside the band
        # plus one step (when it enters and stays)
        last_outside_idx = outside_band_idx[-1]
        if last_outside_idx + 1 < len(time):
            metrics["settling_time"] = float(time[last_outside_idx + 1])
    else:
        # Started within band and never left
        metrics["settling_time"] = 0.0

    # 4. Steady-state error
    metrics["steady_state_error"] = float(abs(setpoint - response[-1]))
    
    # 5. Control Energy (Integral of u^2 dt)
    dt = time[1] - time[0] if len(time) > 1 else 0.02
    metrics["control_energy"] = float(np.sum(control_effort**2) * dt)
    
    # 6. ITAE (Integral of Time-weighted Absolute Error)
    metrics["itae"] = float(np.sum(time * error) * dt)
    
    return metrics
