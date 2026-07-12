def get_wind_class(wind_speed):
    if wind_speed < 4:
        return "Class 1", "Poor"
    elif wind_speed < 5:
        return "Class 2", "Marginal"
    elif wind_speed < 6:
        return "Class 3", "Moderate"
    elif wind_speed < 7:
        return "Class 4", "Good"
    else:
        return "Class 5+", "Excellent"