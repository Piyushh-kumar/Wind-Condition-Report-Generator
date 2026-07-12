import streamlit as st
import folium
import plotly.express as px
import pandas as pd

from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from reverse_geocode import get_address
from geoapify_geocode import get_coordinates
from gwa_lookup import get_all_wind_speeds
from power_lookup import get_all_power_densities
from calculations import interpolate
from autocomplete import get_suggestions
from wind_class import get_wind_class
from site_score import calculate_site_score
from capacity_factor import estimate_capacity_factor
from aep import estimate_aep
from recommendation import get_recommendation
from area_scan import scan_area
from map_visualization import add_wind_points

# New terrain, roughness, and advanced reporting integrations
from terrain import get_elevation, get_slope, get_terrain_rating
from report_generator import generate_report
from roughness_analyzer import analyze_surface_roughness

st.set_page_config(
    page_title="Wind AI - Siting Platform",
    page_icon="🌬️",
    layout="wide"
)

st.title("🌬️ Wind AI Siting & Installation Platform")
st.markdown("Commercial-grade resource assessment optimization tool for micro-siting installations.")
st.divider()

# Sidebar Configuration Controls
st.sidebar.header("⚙️ Simulation Settings")
hub_height = st.sidebar.slider("Turbine Mount Mast Height (m)", min_value=2, max_value=50, value=6)
scan_radius = st.sidebar.selectbox("Scanning Boundary Radius", [0.25, 0.5, 1.0, 2.0, 3.0], index=2, format_func=lambda x: f"{x} km")
turbine_rating = st.sidebar.selectbox("Turbine Core Rating (MW)", [1, 2, 3, 4, 5], index=2)

st.sidebar.divider()
st.sidebar.header("🏢 Rooftop Installation Options")
on_building = st.sidebar.checkbox("Is Rooftop/Structure Mount?", value=True)
building_height = 0.0
wall_height = 0.0

if on_building:
    building_height = st.sidebar.number_input("Structure Roof Elevation Height (m)", min_value=0.0, max_value=100.0, value=12.0, step=1.0)
    wall_height = st.sidebar.number_input("Terrace Parapet Wall Height (m)", min_value=0.0, max_value=5.0, value=1.2, step=0.1)

st.subheader("Choose Assessment Location")
search_text = st.text_input("Search Coordinates, Address, Village, or Coastal Area", key="location_search_input")

# Initialize session state variables safely
if "lat" not in st.session_state: st.session_state.lat = None
if "lon" not in st.session_state: st.session_state.lon = None
if "analysis_run" not in st.session_state: st.session_state.analysis_run = False
if "scan_run" not in st.session_state: st.session_state.scan_run = False
if "selected_suggestion" not in st.session_state: st.session_state.selected_suggestion = None
if "top_data_cache" not in st.session_state: st.session_state.top_data_cache = None

if len(search_text) >= 2:
    suggestions = get_suggestions(search_text)
    if suggestions:
        if search_text not in suggestions:
            suggestions.insert(0, search_text)
            
        current_selection = st.selectbox("Matching Location Suggestions", suggestions, index=0)
        
        if current_selection != st.session_state.selected_suggestion:
            st.session_state.selected_suggestion = current_selection
            try:
                result = get_coordinates(current_selection)
                if result:
                    st.session_state.lat, st.session_state.lon = result
                    st.session_state.analysis_run = False
                    st.session_state.scan_run = False
                    st.session_state.top_data_cache = None
                    st.toast(f"📍 Target Updated: {current_selection}", icon="✅")
                    st.rerun()
            except Exception as e:
                st.error(f"Geocoding Error: {str(e)}")
    else:
        suggestions = [search_text]
        current_selection = st.selectbox("Matching Location Suggestions", suggestions, index=0)
        if current_selection != st.session_state.selected_suggestion:
            st.session_state.selected_suggestion = current_selection
            try:
                result = get_coordinates(current_selection)
                if result:
                    st.session_state.lat, st.session_state.lon = result
                    st.session_state.analysis_run = False
                    st.session_state.scan_run = False
                    st.session_state.top_data_cache = None
                    st.rerun()
            except Exception:
                pass

col1, col2 = st.columns(2)
gps_button = col1.button("📍 Track My Current Location", width="stretch")
map_reset = col2.button("🗺️ Reset to Map Center", width="stretch")

if gps_button:
    location = get_geolocation()
    if location:
        st.session_state.lat = location["coords"]["latitude"]
        st.session_state.lon = location["coords"]["longitude"]
        st.session_state.analysis_run = False
        st.session_state.scan_run = False
        st.session_state.top_data_cache = None
        st.success("GPS Hardware Link Established.")
        st.rerun()
    else:
        st.warning("Please grant browser location tracking permissions and try again.")

if map_reset:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.analysis_run = False
    st.session_state.scan_run = False
    st.session_state.selected_suggestion = None
    st.session_state.top_data_cache = None
    st.rerun()

lat = st.session_state.lat
lon = st.session_state.lon

st.subheader("Interactive GIS Micro-Siting Map")
m = folium.Map(location=[lat if lat is not None else 20.5937, lon if lon is not None else 78.9629], zoom_start=8 if lat is not None else 5)
folium.TileLayer("OpenStreetMap").add_to(m)
folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri", name="Satellite View").add_to(m)

if lat is not None and lon is not None:
    folium.Marker([lat, lon], tooltip="Selected Siting Axis").add_to(m)

folium.LayerControl().add_to(m)
map_data = st_folium(m, height=450, width=None)

if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]
    
    if clicked_lat != st.session_state.lat or clicked_lon != st.session_state.lon:
        st.session_state.lat = clicked_lat
        st.session_state.lon = clicked_lon
        st.session_state.analysis_run = False
        st.session_state.top_data_cache = None
        st.rerun()

if lat is not None and lon is not None:
    address = get_address(lat, lon)
    st.info(f"📍 **Selected Location:** {address} | **Lat:** {lat:.6f}, **Lon:** {lon:.6f}")

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🚀 Execute Comprehensive Wind Assessment", width="stretch"):
            st.session_state.analysis_run = True
    with c_btn2:
        if st.button("🔍 Scan Surrounding Proximity For Alternates", width="stretch"):
            st.session_state.scan_run = True

# --------------------------------------------------
# NEARBY AREA MICRO-SCAN DISCOVERY ENGINE
# --------------------------------------------------
if lat is not None and lon is not None and st.session_state.scan_run:
    st.header("🔍 High-Yield Hotspot Micro-Scan")
    with st.spinner("Analyzing spatial mesh coordinates for localized high-velocity nodes..."):
        results = scan_area(lat, lon, hub_height, scan_radius)
        st.success(f"Grid Scan complete. Evaluated {len(results)} distinct spatial micro-points.")

        scan_map = folium.Map(location=[lat, lon], zoom_start=14)
        folium.TileLayer("OpenStreetMap").add_to(scan_map)
        scan_map = add_wind_points(scan_map, results)
        st_folium(scan_map, height=500, width=None)

        st.subheader("🏆 Top Optimization Coordinates For Installation")
        top_sites = sorted(results, key=lambda x: x["wind"], reverse=True)[:10]
        top_data = [{"Rank": i, "Wind Speed (m/s)": round(s["wind"], 2), "Latitude": round(s["lat"], 6), "Longitude": round(s["lon"], 6)} for i, s in enumerate(top_sites, start=1)]
        st.dataframe(pd.DataFrame(top_data), width="stretch")
        
        # Cache results into session state to preserve data across downloader refreshes
        st.session_state.top_data_cache = top_data

# --------------------------------------------------
# COMPREHENSIVE ASSESSMENT TARGET ANALYSIS PANEL
# --------------------------------------------------
if lat is not None and lon is not None and st.session_state.analysis_run:
    st.divider()
    try:
        winds = get_all_wind_speeds(lat, lon)
        powers = get_all_power_densities(lat, lon)

        roughness_mult, feature_type, feature_desc = analyze_surface_roughness(lat, lon, building_height, wall_height)

        wind_speed = interpolate(hub_height, winds, building_height) * roughness_mult
        power_density = interpolate(hub_height, powers, building_height) * (roughness_mult ** 3)
        
        elevation = get_elevation(lat, lon)
        slope = get_slope(lat, lon)
        terrain_rating = get_terrain_rating(slope)

        wind_class, rating_desc = get_wind_class(wind_speed)
        site_score = calculate_site_score(wind_speed, power_density)
        verdict, application = get_recommendation(wind_speed, power_density, site_score)

        capacity_factor = estimate_capacity_factor(wind_speed)
        aep = estimate_aep(turbine_rating, capacity_factor)

        st.header("📋 Technical Feasibility Profile Summary")
        
        # Build configuration package dict for the PDF generator
        current_settings = {
            "mast_height": hub_height,
            "radius": scan_radius,
            "turbine_rating": turbine_rating,
            "on_building": on_building,
            "building_height": building_height,
            "wall_height": wall_height
        }

        pdf_filename = "Wind_AI_Siting_Report.pdf"
        generate_report(
            filename=pdf_filename, lat=lat, lon=lon, elevation=elevation,
            wind_speed=wind_speed, power_density=power_density, wind_class=wind_class,
            site_score=site_score, verdict=verdict, application=application,
            settings_dict=current_settings, winds_dict=winds, powers_dict=powers,
            top_sites_list=st.session_state.top_data_cache
        )
        
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(label="📥 Download Engineering Feasibility Report (PDF)", data=pdf_file, file_name=pdf_filename, mime="application/pdf")

        v1, v2, v3 = st.columns(3)
        v1.metric("Site Yield Categorization", verdict)
        v2.metric("Recommended Target Deployment", application)
        v3.metric("Terrain Safety Clearance", terrain_rating)

        st.info(f"🛰️ **Satellite Land-Cover Analysis:** Detected **{feature_type}** | *{feature_desc}* (Applied Friction Multiplier: **{roughness_mult}x**)")

        if on_building and hub_height <= wall_height:
            st.error(f"⚠️ Installation Hazard: Mount height ({hub_height}m) is lower than or equal to the parapet wall ({wall_height}m). Turbine will suffer severe boundary-vortex wake stress!")
        elif slope > 15:
            st.error(f"⚠️ Extreme Slope Danger: ({slope:.1f}°). High structural logistics risk.")
        else:
            st.success("Resource criteria meet target operational thresholds for deployment.")

        st.subheader("📊 Primary Wind Asset Dynamics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"Effective Velocity @ Hub", f"{wind_speed:.2f} m/s")
        m2.metric(f"Kinetic Power Density", f"{power_density:.0f} W/m²")
        m3.metric("IEC Wind Class ID", wind_class)
        m4.metric("Site Slope Incline", f"{slope:.1f}°")

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Site Siting Score", f"{site_score}/100")
        s2.metric("Turbine Capacity Factor", f"{capacity_factor}%")
        s3.metric("Annualized Generation Yield (AEP)", f"{aep/1000:.1f} MWh")
        s4.metric("Base Ground Elevation", f"{elevation:.0f} m")

        st.divider()
        ch1, ch2 = st.columns(2)
        heights = [10, 50, 100, 150, 200]
        
        with ch1:
            st.subheader("📈 Vertical Velocity Shear Profile")
            w_vals = [winds["10m"], winds["50m"], winds["100m"], winds["150m"], winds["200m"]]
            fig = px.line(pd.DataFrame({"Height (m)": heights, "Speed (m/s)": w_vals}), x="Height (m)", y="Speed (m/s)", markers=True)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch")
            
        with ch2:
            st.subheader("📈 Vertical Power Distribution Profile")
            p_vals = [powers["10m"], powers["50m"], powers["100m"], powers["150m"], powers["200m"]]
            fig2 = px.line(pd.DataFrame({"Height (m)": heights, "Power (W/m²)": p_vals}), x="Height (m)", y="Power (W/m²)", markers=True)
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, width="stretch")

    except Exception as e:
        st.error(f"Data Ingestion Pipeline Execution Error: {str(e)}")