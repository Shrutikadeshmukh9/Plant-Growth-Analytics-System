from databases import Database
from typing import List
from sqlalchemy import MetaData, Table, Column, String, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

# Initialize database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/plants"
database = Database(DATABASE_URL)


metadata = MetaData()

plant_readings = Table(
    'plant_readings',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default="uuid_generate_v4()"),  
    Column('timestamp', DateTime),
    Column('zone_id', String),
    Column('plant_id', String),
    Column('temperature', Float),
    Column('humidity', Float),
    Column('soil_moisture', Float),
    Column('light_level', Float),
    Column('plant_height', Float, nullable=True),
    Column('leaf_count', Integer, nullable=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

# Connect to the database when the app starts
async def connect():
    await database.connect()

# Disconnect from the database when the app shuts down
async def disconnect():
    await database.disconnect()

# Function to insert sensor data into the database
async def add_single_sensor_data(sensor_data: dict):
    query = plant_readings.insert().values(sensor_data)
    await database.execute(query)

# Function to insert multiple sensor data (batch ingestion)
async def add_batch_sensor_data(sensor_data_list: List[dict]):
    query = plant_readings.insert()
    await database.execute_many(query, sensor_data_list)

# Function to fetch sensor data by plant_id
async def get_data_by_plant_id(plant_id: str):
    query = plant_readings.select().where(plant_readings.c.plant_id == plant_id)
    return await database.fetch_all(query)

# Function to fetch sensor data by species_id
async def get_data_by_species(species_id: str):
    query = plant_readings.select().where(plant_readings.c.plant_id.like(f"{species_id}%"))
    return await database.fetch_all(query)

# Function to fetch sensor data by zone_id
async def get_sensor_data_by_zone(zone_id: str):
    query = plant_readings.select().where(plant_readings.c.zone_id == zone_id)
    return await database.fetch_all(query)

# Function to fetch sensor data by zone_id and plant_name
async def get_sensor_data_by_zone_and_plant(zone_id: str, plant_name: str):
    if "_" in plant_name:
        query = plant_readings.select().where(
            (plant_readings.c.zone_id == zone_id) & (plant_readings.c.plant_id == plant_name)
        )
    else:
        query = plant_readings.select().where(
            (plant_readings.c.zone_id == zone_id) & (plant_readings.c.plant_id.like(f"{plant_name}%"))
        )
    return await database.fetch_all(query)
