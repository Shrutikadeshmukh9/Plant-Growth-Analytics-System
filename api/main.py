import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.openapi.utils import get_openapi
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from statistics import mean
import numpy as np
from . import database  # prevent circular imports

app = FastAPI()

# JWT Settings 
class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTHJWT_SECRET_KEY", "default_dev_key")  

@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Data Models
class SensorData(BaseModel):
    timestamp: str
    zone_id: str
    plant_id: str
    temperature: float
    humidity: float
    soil_moisture: float
    light_level: float
    plant_height: float = None
    leaf_count: int = None

class LoginModel(BaseModel):
    username: str
    password: str

# Normalization of sensor data
def normalize_data(sensor_data: dict) -> dict:
    sensor_data["temperature"] = (sensor_data["temperature"] - 10) / (40 - 10)  # Normalizing temperature (example range: 10–40°C)
    sensor_data["humidity"] = sensor_data["humidity"] / 100  # Normalizing humidity (percentage)
    sensor_data["soil_moisture"] = min(max(sensor_data["soil_moisture"], 0), 1)  # Soil moisture to 0–1 range
    sensor_data["light_level"] = min(max(sensor_data["light_level"], 0), 1)  # Light level to 0–1 range
    return sensor_data

@app.post("/login")
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    if user.username == "admin" and user.password == "password":
        access_token = Authorize.create_access_token(subject=user.username)
        return {"access_token": access_token}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/v1/sensor-data/single")
async def add_single_sensor_data_endpoint(sensor_data: SensorData, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    sensor_data_dict = normalize_data(sensor_data.dict())
    sensor_data_dict['timestamp'] = datetime.fromisoformat(sensor_data.timestamp)
    await database.add_single_sensor_data(sensor_data_dict)
    return {"message": "Single sensor data added successfully!"}

@app.post("/api/v1/sensor-data/batch")
async def add_batch_sensor_data_endpoint(sensor_data_list: List[SensorData], Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    sensor_data_dicts = [
        {**normalize_data(sensor_data.dict()), "timestamp": datetime.fromisoformat(sensor_data.timestamp)}
        for sensor_data in sensor_data_list
    ]
    await database.add_batch_sensor_data(sensor_data_dicts)
    return {"message": "Batch sensor data added successfully!"}

@app.get("/api/v1/sensor-data/{zone_id}")
async def get_sensor_data_by_zone_endpoint(zone_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    data = await database.get_sensor_data_by_zone(zone_id)
    return {"zone_id": zone_id, "data": data}

@app.get("/api/v1/sensor-data/{zone_id}/{plant_name}")
async def get_sensor_data_by_zone_and_plant_endpoint(zone_id: str, plant_name: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    data = await database.get_sensor_data_by_zone_and_plant(zone_id, plant_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for plant_name: {plant_name} in zone_id: {zone_id}")
    return {"zone_id": zone_id, "plant_name": plant_name, "data": data}

# Analytics Endpoint for Growth Rate
@app.get("/api/v1/analytics/growth-rate/{plant_id}")
async def growth_rate_analytics(plant_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    data = await database.get_data_by_plant_id(plant_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for the given plant_id.")
    
    sorted_data = sorted(data, key=lambda x: x["timestamp"])
    growth_rates = []
    for i in range(1, len(sorted_data)):
        height_current = float(sorted_data[i]["plant_height"]) if sorted_data[i]["plant_height"] is not None else None
        height_previous = float(sorted_data[i - 1]["plant_height"]) if sorted_data[i - 1]["plant_height"] is not None else None
        
        if height_current is not None and height_previous is not None:
            height_diff = height_current - height_previous
            time_diff = (sorted_data[i]["timestamp"] - sorted_data[i - 1]["timestamp"]).total_seconds() / 86400
            if time_diff > 0:
                growth_rates.append(height_diff / time_diff)
    
    if len(growth_rates) < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough data to compute growth rate trends or correlations."
        )

    environmental_factors = {
        "temperature": [float(d["temperature"]) for d in sorted_data if d["temperature"] is not None],
        "humidity": [float(d["humidity"]) for d in sorted_data if d["humidity"] is not None],
        "light_level": [float(d["light_level"]) for d in sorted_data if d["light_level"] is not None],
    }
    
    correlations = {}
    for factor, values in environmental_factors.items():
        if len(values) >= 2:
            correlations[factor] = np.corrcoef(growth_rates, values[:len(growth_rates)])[0, 1]
        else:
            correlations[factor] = None

    return {
        "plant_id": plant_id,
        "average_growth_rate": mean(growth_rates) if growth_rates else 0,
        "growth_rate_trends": growth_rates,
        "environmental_correlations": correlations,
    }

# Analytics Endpoint for Optimal Conditions
@app.get("/api/v1/analytics/optimal-conditions/{species_id}")
async def optimal_conditions_analytics(species_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    data = await database.get_data_by_species(species_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for the given species_id.")
    
    temperatures = [d["temperature"] for d in data if d["temperature"] is not None]
    humidities = [d["humidity"] for d in data if d["humidity"] is not None]
    soil_moistures = [d["soil_moisture"] for d in data if d["soil_moisture"] is not None]

    return {
        "species_id": species_id,
        "optimal_conditions": {
            "temperature_range": (min(temperatures), max(temperatures)) if temperatures else None,
            "humidity_range": (min(humidities), max(humidities)) if humidities else None,
            "soil_moisture_range": (min(soil_moistures), max(soil_moistures)) if soil_moistures else None,
        },
    }

# Analytics Endpoint for Yield Prediction
@app.get("/api/v1/analytics/yield-prediction/{zone_id}")
async def yield_prediction_analytics(zone_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    data = await database.get_sensor_data_by_zone(zone_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for the given zone_id.")
    
    plant_heights = [d["plant_height"] for d in data if d["plant_height"] is not None]
    if not plant_heights:
        raise HTTPException(status_code=400, detail="Not enough data to calculate yield prediction.")
    
    average_height = mean(plant_heights)
    yield_prediction = len(plant_heights) * average_height  

    target_date = (datetime.utcnow() + timedelta(days=30)).strftime("%B %Y")
    suggestions = "Consider optimizing temperature and humidity for better yield."

    return {
        "zone_id": zone_id,
        "predicted_yield": round(yield_prediction, 2),
        "prediction_timeframe": f"By {target_date}",
        "suggestions": suggestions,
    }

@app.get("/health-check")
async def health_check():
    return {"status": "ok"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Plant Monitoring System",
        version="1.0.0",
        description="API for Plant Monitoring with JWT Authentication and Analytics",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
