from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI(title="Thermal Data API")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Python array containing the Celsius data to the backend
try:
    # Load the data
    celsius_matrix = np.load("./data_thermal/tokio_celsius.npy")

    # Clean up data
    celsius_matrix = np.where(np.isnan(celsius_matrix), None, celsius_matrix)
except FileNotFoundError:
    print("Error: Satellite data not found. Please run the thermal conversion script first.")
    celsius_matrix = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Thermal Data API. Use /api/temperature to get the temperature data."}

@app.get("/api/temperature")
def get_temperature_data():
    if celsius_matrix is None:
        return {"error": "Temperature data not available. Please run the thermal conversion script first."}
    else:   
        return {
            "city": "Tokio",
            "date": "06.08.2015",
            "resolution": "30m per pixel",
            "max_temp": float(np.nanmax(celsius_matrix)),
            "min_temp": float(np.nanmin(celsius_matrix)),
            "data": celsius_matrix.tolist()
        }