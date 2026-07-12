import folium
from folium.plugins import HeatMap

def add_wind_points(m, results):
    if not results:
        return m

    heat_data = []

    # Find the top-performing node for micro-siting positioning
    best_point = max(results, key=lambda x: x["wind"])
    min_wind = min(p["wind"] for p in results)
    max_wind = max(p["wind"] for p in results)
    wind_range = max(max_wind - min_wind, 0.001)

    for point in results:
        # Normalize weights safely for Folium's intensity engine
        normalized = (point["wind"] - min_wind) / wind_range
        heat_data.append([point["lat"], point["lon"], normalized])

    # 1. ADD GRADIENT HEATMAP OVERLAY WITH NATURAL CONTROURS
    # Adjusting radius and blur removes the "blocky rectangle" artifact seen in raw grids
    HeatMap(
        heat_data,
        radius=25,          # Increased for smoother blending between grid rows
        blur=15,            # Higher blur creates organic fluid dynamics curves
        min_opacity=0.25,
        max_zoom=18,
        gradient={
            0.0: '#0000ff', # Deep blue for lower threshold speeds
            0.4: '#00ffff', # Cyan
            0.6: '#00ff00', # Green for moderate operational yield
            0.8: '#ffff00', # Yellow
            1.0: '#ff0000'  # Vivid red for prime high-velocity turbine locations
        }
    ).add_to(m)

    # 2. ADD AN EXTENDED CONTENT POPUP MARKER FOR THE OPTIMAL TURBINE AXIS
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; width: 180px; font-size: 12px; color: #333;">
        <h4 style="margin: 0 0 5px 0; color: #d9534f; border-bottom: 1px solid #ccc; padding-bottom: 3px;">
            ⭐ Prime Siting Axis
        </h4>
        <b>Latitude:</b> {best_point['lat']:.5f}<br>
        <b>Longitude:</b> {best_point['lon']:.5f}<br>
        <span style="font-size: 13px; color: #000;">
            <b>Peak Velocity:</b> <span style="color:#d9534f;"><b>{best_point['wind']:.2f} m/s</b></span>
        </span>
    </div>
    """

    folium.Marker(
        location=[best_point["lat"], best_point["lon"]],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip="Click to view installation analytics",
        icon=folium.Icon(
            color="red",
            icon="flash", # Clean lightning bolt / power generation symbol
            icon_color="white",
            prefix="fa" # Uses FontAwesome styling engine natively
        )
    ).add_to(m)

    # 3. EMBED A FLOATING VISUAL COLOR SCALE LEGEND
    # This gives prospective land owners and investors instant data context directly on screen
    legend_html = f"""
     <div style="
     position: fixed; 
     bottom: 50px; left: 50px; width: 160px; height: 140px; 
     background-color: white; border: 2px solid grey; z-index:9999; font-size:12px;
     font-family: Arial, sans-serif; padding: 10px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
     ">
     <b style="color: #444;">Wind Velocity Scale</b><br>
     <div style="margin-top: 8px;">
         <i style="background: #ff0000; width: 18px; height: 12px; float: left; margin-right: 8px; border-radius:2px;"></i> Max Yield ({max_wind:.1f} m/s)<br>
         <i style="background: #ffff00; width: 18px; height: 12px; float: left; margin-right: 8px; border-radius:2px;"></i> High Velocity<br>
         <i style="background: #00ff00; width: 18px; height: 12px; float: left; margin-right: 8px; border-radius:2px;"></i> Moderate Yield<br>
         <i style="background: #00ffff; width: 18px; height: 12px; float: left; margin-right: 8px; border-radius:2px;"></i> Marginal Resource<br>
         <i style="background: #0000ff; width: 18px; height: 12px; float: left; margin-right: 8px; border-radius:2px;"></i> Min Velocity ({min_wind:.1f} m/s)<br>
     </div>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m