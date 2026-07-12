import base64
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import resend

from gwa_lookup import get_all_wind_speeds
from power_lookup import get_all_power_densities
from calculations import interpolate
from report_generator import generate_report

app = FastAPI()

# Enable CORS so your React site can talk to this API
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

resend.api_key = os.environ.get("RESEND_API_KEY")

class AssessmentRequest(BaseModel):
    email: str
    location: str
    mast_height: float

@app.post("/generate-report")
async def generate_report_api(req: AssessmentRequest):
    # Placeholder coordinates; replace with your geocoding logic if needed
    lat, lon = 26.4499, 80.3319 
    
    winds = get_all_wind_speeds(lat, lon)
    # powers = get_all_power_densities(lat, lon) # Uncomment if used
    wind_speed = interpolate(req.mast_height, winds)
    
    # Generate PDF
    pdf_path = "Wind_AI_Siting_Report.pdf"
    generate_report(pdf_path, lat, lon, 100, wind_speed, 500, "Class I", 85, "Good", "Roof", {})
    
    # Read and encode PDF for attachment
    with open(pdf_path, "rb") as pdf_file:
        encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    # Email to User
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": req.email,
        "subject": "Your Wind AI Site Assessment",
        "html": "<p>Your assessment report is attached.</p>",
        "attachments": [
            {
                "filename": "Report.pdf",
                "content": encoded_pdf
            }
        ]
    })
    return {"status": "success"}