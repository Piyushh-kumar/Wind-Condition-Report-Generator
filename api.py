from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import resend
import os

# UPDATED IMPORTS:
from gwa_lookup import get_all_wind_speeds  # Correct file for wind data
from power_lookup import get_all_power_densities # Correct file for power data
from calculations import interpolate
from report_generator import generate_report

app = FastAPI()

# Enable CORS so your React site can talk to this API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

resend.api_key = os.environ.get("RESEND_API_KEY") # Ensure this is read from environment variables

class AssessmentRequest(BaseModel):
    email: str
    location: str # Assuming location is a string or handle coordinate extraction here
    mast_height: float

@app.post("/generate-report")
async def generate_report_api(req: AssessmentRequest):
    # This assumes location string format might need parsing; 
    # adjust based on how your geocoding works
    lat, lon = 26.4499, 80.3319 # Placeholder: Update with your geocoding logic
    
    winds = get_all_wind_speeds(lat, lon)
    powers = get_all_power_densities(lat, lon)
    wind_speed = interpolate(req.mast_height, winds)
    
    # Generate PDF
    pdf_path = "Wind_AI_Siting_Report.pdf"
    generate_report(pdf_path, lat, lon, 100, wind_speed, 500, "Class I", 85, "Good", "Roof", {})
    
    # Email to User
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": req.email,
        "subject": "Your Wind AI Site Assessment",
        "html": "<p>Your assessment report is attached.</p>",
        "attachments": [{"filename": "Report.pdf", "content": open(pdf_path, "rb").read()}]
    })
    return {"status": "success"}