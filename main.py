from typing import Union

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from eicr_package.eicr_processor import process_eicr_pdf
import tempfile

app = FastAPI()

# Add website origins that are allowed to access the API
# Include url that will host the frontend application with the port for local development
# When deployed the url should be added here
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "OK"}

@app.post("/process-pdf")
async def process_pdf(request: Request):
    form = await request.form()
    uploaded_file = list(form.values())[0]
    filename = uploaded_file.filename
    print(f"Uploaded file: {filename}")
    file_contents = await uploaded_file.read()
     # Save uploaded pdf temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(file_contents)
        temp_pdf_path = f.name

    # Run processing
    output_data = process_eicr_pdf(temp_pdf_path)
    print(f"Output data: {output_data}")
    return output_data
