def estimate_aep(
    turbine_capacity_mw,
    capacity_factor
):

    annual_energy = (
        turbine_capacity_mw
        * 1000
        * 8760
        * (capacity_factor / 100)
    )

    return annual_energy