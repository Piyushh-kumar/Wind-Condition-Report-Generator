from gwa_lookup import get_all_wind_speeds
from power_lookup import get_all_power_densities
from calculations import interpolate
from terrain import get_elevation, get_slope, get_terrain_rating
from wind_class import get_wind_class
from site_score import calculate_site_score
from recommendation import get_recommendation

# Inject the new satellite landscape analyzer module
from roughness_analyzer import analyze_surface_roughness

def scan_point(lat, lon, hub_height):
    winds = get_all_wind_speeds(lat, lon)
    powers = get_all_power_densities(lat, lon)

    raw_wind_speed = interpolate(hub_height, winds)
    
    # Dynamic landscape friction adjustment applied here!
    roughness_multiplier, terrain_feature, description = analyze_surface_roughness(lat, lon)
    wind_speed = raw_wind_speed * roughness_multiplier
    
    power_density = interpolate(hub_height, powers) * (roughness_multiplier ** 3) # Cubic scale adjustment

    elevation = get_elevation(lat, lon)
    slope = get_slope(lat, lon)
    terrain_rating = get_terrain_rating(slope)

    wind_class, rating_desc = get_wind_class(wind_speed)
    site_score = calculate_site_score(wind_speed, power_density)
    verdict, application = get_recommendation(wind_speed, power_density, site_score)

    return {
        "wind_speed": wind_speed,
        "power_density": power_density,
        "elevation": elevation,
        "slope": slope,
        "terrain_rating": terrain_rating,
        "wind_class": wind_class,
        "site_score": site_score,
        "verdict": verdict,
        "application": application
    }

def scan_wind_only(lat, lon, hub_height):
    winds = get_all_wind_speeds(lat, lon)
    return interpolate(hub_height, winds)