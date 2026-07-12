import requests

def analyze_surface_roughness(lat, lon, building_height=0.0, wall_height=0.0):
    """
    Scans surrounding terrain and overlays specific building parameters
    to compute micro-siting speedup vs turbulence risk adjustments.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:15];
    (
      node["natural"](around:500, {lat}, {lon});
      way["natural"](around:500, {lat}, {lon});
      node["landuse"](around:500, {lat}, {lon});
      way["landuse"](around:500, {lat}, {lon});
      node["water"](around:500, {lat}, {lon});
      way["water"](around:500, {lat}, {lon});
    );
    out tags;
    """
    
    # Establish structural coefficients based on input specs
    structural_multiplier = 1.0
    structural_note = ""
    
    if building_height > 0:
        # Building roof compression creates a clean edge speedup effect (~8-15% increase)
        structural_multiplier += 0.12
        structural_note = f"Structure speedup active (+12% via {building_height}m G+3 compression zone)."
        
        if wall_height > 0:
            # A tall parapet wall introduces localized recirculation shear stress (-5% velocity correction penalty)
            structural_multiplier -= 0.05
            structural_note += f" Warning: {wall_height}m boundary wall creates micro-vortex turbulence. Clear rotor hub above wall."

    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=8)
        if response.status_code != 200:
            return 1.0 * structural_multiplier, "Standard Grid", f"Baseline atmospheric matrix. {structural_note}"
            
        elements = response.json().get("elements", [])
        forest_count = 0
        water_count = 0
        urban_count = 0
        
        for el in elements:
            tags = el.get("tags", {})
            if tags.get("natural") in ["wood", "scrub"] or tags.get("landuse") in ["forest"]:
                forest_count += 1
            elif tags.get("natural") in ["water"] or tags.get("water") != "":
                water_count += 1
            elif tags.get("landuse") in ["industrial", "commercial", "residential"]:
                urban_count += 1

        if water_count > forest_count and water_count > urban_count:
            return 1.12 * structural_multiplier, "Low Friction Coastal/River Zone", f"Accelerated fluid flow near water. {structural_note}"
        elif forest_count > urban_count and forest_count >= 1:
            return 0.88 * structural_multiplier, "High Roughness Tree Canopy", f"Friction from tree shelter active. {structural_note}"
        elif urban_count >= 1:
            return 0.82 * structural_multiplier, "Dense Urban Complex", f"Heavy structural roughness profile present. {structural_note}"
            
        return 1.0 * structural_multiplier, "Open Flat Ground", f"Standard landscape boundary clearance. {structural_note}"
        
    except Exception:
        return 1.0 * structural_multiplier, "Standard Grid (Fallback)", f"Atmospheric matrix default. {structural_note}"