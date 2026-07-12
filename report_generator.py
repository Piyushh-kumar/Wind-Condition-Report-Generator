import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import plotly.graph_objects as go

def generate_report(
    filename,
    lat,
    lon,
    elevation,
    wind_speed,
    power_density,
    wind_class,
    site_score,
    verdict,
    application,
    settings_dict,
    winds_dict=None,
    powers_dict=None,
    top_sites_list=None
):
    # Setup document with 0.75-inch margins
    doc = SimpleDocTemplate(
        filename,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )
    
    styles = getSampleStyleSheet()
    elements = []

    # Typography Styling Definitions
    company_style = ParagraphStyle('Comp', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor("#0f2c59"))
    subtitle_style = ParagraphStyle('Sub', fontName='Helvetica', fontSize=10, leading=12, textColor=colors.HexColor("#555555"))
    title_style = ParagraphStyle('TitleStyle', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor("#1a1a1a"), spaceAfter=2)
    section_heading = ParagraphStyle('SectHead', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor("#0f2c59"), spaceBefore=12, spaceAfter=6, keepWithNext=True)
    label_style = ParagraphStyle('Lbl', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor("#333333"))
    value_style = ParagraphStyle('Val', fontName='Helvetica', fontSize=9, leading=11, textColor=colors.HexColor("#555555"))
    hdr_style = ParagraphStyle('Hdr', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)

    # 1. BRAND HEADER BAND
    elements.append(Paragraph("MAINI RENEWABLES", company_style))
    elements.append(Paragraph("Siting & Resource Assessment Division", subtitle_style))
    elements.append(Spacer(1, 8))
    
    divider = Table([[""]], colWidths=[7.0 * inch])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.HexColor("#0f2c59")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 10))

    # 2. DOCUMENT HEADER
    elements.append(Paragraph("Wind Resource Site Assessment", title_style))
    elements.append(Paragraph("Confidential Micro-Siting Feasibility Analysis", subtitle_style))
    elements.append(Spacer(1, 12))

    # 3. CONFIGURATION SETTINGS SECTION
    elements.append(Paragraph("Simulation & System Settings", section_heading))
    settings_data = [
        [Paragraph("Turbine Mount Mast Height", label_style), Paragraph(f"{settings_dict.get('mast_height', 10)} m", value_style)],
        [Paragraph("Scanning Proximity Radius", label_style), Paragraph(f"{settings_dict.get('radius', 1.0)} km", value_style)],
        [Paragraph("Turbine Core Rating", label_style), Paragraph(f"{settings_dict.get('turbine_rating', 3)} MW", value_style)],
        [Paragraph("Rooftop Structure Mount", label_style), Paragraph("Yes" if settings_dict.get('on_building') else "No", value_style)]
    ]
    if settings_dict.get('on_building'):
        settings_data.append([Paragraph("Structure Roof Elevation", label_style), Paragraph(f"{settings_dict.get('building_height')} m", value_style)])
        settings_data.append([Paragraph("Terrace Parapet Wall Height", label_style), Paragraph(f"{settings_dict.get('wall_height')} m", value_style)])

    settings_table = Table(settings_data, colWidths=[2.5 * inch, 4.5 * inch])
    settings_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f3f5")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#dee2e6"))
    ]))
    elements.append(settings_table)

    # 4. PRIMARY ANALYTICS TARGET METRICS
    elements.append(Paragraph("Geographical & Yield Resource Metrics", section_heading))
    metrics_data = [
        [Paragraph("Target Coordinates", label_style), Paragraph(f"Lat: {lat:.6f}°, Lon: {lon:.6f}°", value_style)],
        [Paragraph("Base Ground Elevation", label_style), Paragraph(f"{elevation:.0f} m", value_style)],
        [Paragraph("Adjusted Wind Velocity", label_style), Paragraph(f"{wind_speed:.2f} m/s", value_style)],
        [Paragraph("Kinetic Power Density", label_style), Paragraph(f"{power_density:.0f} W/m²", value_style)],
        [Paragraph("IEC Wind Class ID", label_style), Paragraph(str(wind_class), value_style)],
        [Paragraph("Total Siting Score", label_style), Paragraph(f"{site_score} / 100", value_style)],
        [Paragraph("Siting Verdict", label_style), Paragraph(str(verdict), value_style)],
        [Paragraph("Recommended Deployment", label_style), Paragraph(str(application), value_style)]
    ]
    metrics_table = Table(metrics_data, colWidths=[2.5 * inch, 4.5 * inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('BACKGROUND', (0,-2), (-1,-1), colors.HexColor("#edf2f7")) # Highlight verdict blocks
    ]))
    elements.append(metrics_table)

    # 5. CHARTS INJECTION POINT (Velocity Shear Profile)
    if winds_dict and powers_dict:
        elements.append(Paragraph("Atmospheric Boundary Profiles", section_heading))
        heights = [10, 50, 100, 150, 200]
        w_vals = [winds_dict["10m"], winds_dict["50m"], winds_dict["100m"], winds_dict["150m"], winds_dict["200m"]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=heights, y=w_vals, name="Wind Speed (m/s)", line=dict(color='#0f2c59', width=3)))
        fig.update_layout(
            title="Vertical Velocity Shear Profile", xaxis_title="Height (m)", yaxis_title="Velocity (m/s)",
            width=650, height=180, margin=dict(l=40, r=40, t=35, b=35),
            paper_bgcolor='rgba(248,249,250,1)', plot_bgcolor='rgba(255,255,255,1)'
        )
        fig.update_xaxes(showgrid=True, gridcolor='#e9ecef')
        fig.update_yaxes(showgrid=True, gridcolor='#e9ecef')
        
        img_bytes = fig.to_image(format="png")
        elements.append(Image(io.BytesIO(img_bytes), width=6.5*inch, height=1.8*inch))
        elements.append(Spacer(1, 10))

    # 6. SURROUNDING SUGGESTIONS / EXCELLENT HOTSPOTS MATRIX
    if top_sites_list:
        elements.append(Paragraph("Micro-Siting Proximity Discovery Matrix (Top 5 Alternate Nodes)", section_heading))
        table_data = [[
            Paragraph("Rank", hdr_style), 
            Paragraph("Latitude", hdr_style), 
            Paragraph("Longitude", hdr_style), 
            Paragraph("Wind Velocity", hdr_style)
        ]]
        
        for site in top_sites_list[:5]:
            table_data.append([
                Paragraph(str(site["Rank"]), value_style),
                Paragraph(f"{site['Latitude']:.6f}°", value_style),
                Paragraph(f"{site['Longitude']:.6f}°", value_style),
                Paragraph(f"{site['Wind Speed (m/s)']:.2f} m/s", value_style)
            ])
            
        nodes_table = Table(table_data, colWidths=[1.0 * inch, 2.0 * inch, 2.0 * inch, 2.0 * inch])
        nodes_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f2c59")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#dee2e6"))
        ]))
        elements.append(nodes_table)

    # 7. REGULATORY FOOTER
    elements.append(Spacer(1, 15))
    disclaimer_style = ParagraphStyle('Foot', fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=colors.HexColor("#718096"))
    elements.append(Paragraph(
        "Notice: This asset documentation has been generated automatically by Maini Renewables analytics "
        "modelling software using spatial wind resource maps derived from the Global Wind Atlas database. "
        "Estimates are simulated to enable targeted rooftop deployment configurations and engineering verification.",
        disclaimer_style
    ))

    doc.build(elements)