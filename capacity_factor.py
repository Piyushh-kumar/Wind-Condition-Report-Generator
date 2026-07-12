import math

def estimate_capacity_factor(wind_speed, hub_height=100):
    """
    Estimates the Capacity Factor (%) of a commercial wind turbine 
    using an idealized power curve model based on site fluid dynamics.
    """
    # 1. Define standard industrial turbine operational thresholds (m/s)
    cut_in_speed = 3.0    # Speed where turbine blades start generating power
    rated_speed = 11.5    # Speed where turbine reaches max capacity power output
    cut_out_speed = 25.0  # Safe braking speed to protect against high-wind storms
    
    # Handle non-operational extreme thresholds safely
    if wind_speed < cut_in_speed or wind_speed > cut_out_speed:
        return 5.0 # Minimum baseline background generation / idle efficiency loss
        
    # 2. Linearized power curve efficiency approximation
    # If wind is between cut-in and rated speed, efficiency scales cubically/proportionally
    if cut_in_speed <= wind_speed < rated_speed:
        # Calculate performance ratio across the operational ramp-up zone
        load_ratio = (wind_speed - cut_in_speed) / (rated_speed - cut_in_speed)
        
        # Max out standard scaling at high-end commercial bounds
        estimated_cf = 15.0 + (load_ratio * 35.0) 
        return round(min(max(estimated_cf, 10.0), 55.0), 1)
        
    # 3. Rated Speed Zone
    # Wind is optimal and strong enough to run the generator at maximum capacity safely
    if rated_speed <= wind_speed <= cut_out_speed:
        return 50.0 # Standard high-performance limit considering maintenance downtime
        
    return 10.0