def interpolate(target_height, values, building_height=0.0):
    """
    Interpolates wind or power data across a vertical column.
    If mounted on a structure, shifts target height using displacement fluid dynamics.
    """
    # Adjust target height if building obstacle displacement applies
    effective_target = target_height + building_height

    heights = [10, 50, 100, 150, 200]

    if effective_target <= 10:
        return values["10m"]

    if effective_target >= 200:
        return values["200m"]

    for i in range(len(heights) - 1):
        h1 = heights[i]
        h2 = heights[i + 1]

        if h1 <= effective_target <= h2:
            v1 = values[f"{h1}m"]
            v2 = values[f"{h2}m"]

            return v1 + ((effective_target - h1) / (h2 - h1)) * (v2 - v1)