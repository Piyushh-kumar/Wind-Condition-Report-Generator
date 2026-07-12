from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import resend
import os
from calculations import get_all_wind_speeds, get_all_power_densities, interpolate
from report_generator import generate_report

app = FastAPI()

# Enable CORS so your React site can talk to this API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

resend.api_key = "YOUR_RESEND_API_KEY"

class AssessmentRequest(BaseModel):
    email: str
    lat: float
    lon: float
    mast_height: float

@app.post("/generate-report")
async def generate_report_api(req: AssessmentRequest):
    # 1. Run your existing engineering logic
    winds = get_all_wind_speeds(req.lat, req.lon)
    powers = get_all_power_densities(req.lat, req.lon)
    wind_speed = interpolate(req.mast_height, winds)
    
    # 2. Generate PDF
    pdf_path = "Wind_AI_Siting_Report.pdf"
    generate_report(pdf_path, req.lat, req.lon, 100, wind_speed, 500, "Class I", 85, "Good", "Roof", {})
    
    # 3. Email to User
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": req.email,
        "subject": "Your Wind AI Site Assessment",
        "html": "<p>Your assessment report is attached.</p>",
        "attachments": [{"filename": "Report.pdf", "content": open(pdf_path, "rb").read()}]
    })
    return {"status": "success"}