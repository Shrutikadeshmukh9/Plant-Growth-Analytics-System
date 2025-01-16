#  Plant Growth Analytics System

---
## 🛠️ About the Project

This project is a technical assessment that involves building a plant monitoring system to process sensor data and provide growth insights. The system is designed to handle sensor data, analyze growth rates, and offer environmental correlations.

---

## 🎯 Key Features
- FastAPI for APIs and analytics.
- PostgreSQL database setup with Docker.
- Environmental normalization for data.
- Growth rate and yield prediction APIs.

---

## 📑 Setup Instructions

### Prerequisites
Before running the project, ensure you have the following installed:
- **Python** (3.8 or higher)
- **[Docker and Docker Compose](https://www.docker.com/get-started)** (for setting up the database)
- **PostgreSQL** (if not using Docker)
- Any text editor or IDE (e.g., VS Code, PyCharm)

---


### Steps to Set Up the Project
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shrutikadeshmukh9/Plant-Growth-Analytics-System.git
   cd Plant-Growth-Analytics-System

2. **Set Up a Virtual Environment**:
   Create and activate a virtual environment for the project:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate

3. **Install Dependencies**:
   Install all the required dependencies for the project:

   ```bash
   pip install -r requirements.txt

4. **Set Up the Database Using Docker**:
   Ensure Docker is running, and then build and start the database:

   ```bash
   docker compose up --build

5. **Verify Database Setup**:
   Use the following Docker command to connect to the PostgreSQL instance:

   ```bash
   docker exec -it plants_db psql -U postgres -d plants
   ```

   - **View the Database**:
     After connecting to the database, you can run the following commands in the `psql` shell:

     - **List all tables**:
       ```sql
       \dt
       ```

     - **View the schema of the `plant_readings` table**:
       ```sql
       \d+ plant_readings
       ```


---

## 📝 Task 1: Database Setup and Optimization

### 🔍 Analysis of the Database Schema

The provided schema for the `plant_readings` table was examined to ensure it aligns with best practices and meets the requirements of a plant monitoring system. Below are the observations and analysis:
 
1. **Existing Schema:**
   - The `plant_readings` table contains the following fields:
     - `id`: A unique identifier for each reading.
     - `zone_id`: Represents the zone where the plant is located.
     - `plant_id`: A unique identifier for each plant.
     - `temperature`, `humidity`, `soil_moisture`, and `light_level`: Sensor readings.
     - `timestamp`: The time when the reading was recorded.
2. **Analysis Plan:**
   - Data Accuracy and Redundancy:
     - Why Relevant?
       - Duplicate or inaccurate data can skew growth insights and analytics like optimal conditions or yield predictions.
     - Query for Redundancy:
       ```bash
       SELECT timestamp, zone_id, plant_id, COUNT(*)
       FROM plant_readings
       GROUP BY timestamp, zone_id, plant_id
       HAVING COUNT(*) > 1;
     - Observation : The dataset shows duplicate entries for each unique combination of timestamp, zone_id, and plant_id, as indicated by a consistent count of 2 for all rows. This suggests a potential data redundancy 
       issue, likely due to missing constraints or errors in the data insertion process, requiring further investigation and cleanup.
   - Query Efficiency for Analytics :
     - Why Relevant?
       - The project involves querying the database for time-series data and zone/plant-specific data. Ensuring these queries are efficient is critical for the REST API and analytics endpoints.
     - Query for Efficiency check:
       ```bash
       EXPLAIN ANALYZE SELECT AVG(temperature), AVG(humidity)
       FROM plant_readings
       WHERE zone_id = 'zone_1' AND timestamp BETWEEN '2024-01-01' AND '2024-02-01';
     - Observation: The execution time is relatively efficient at 48.91 ms, but the sequential scan suggests potential for optimization, such as creating an index on zone_id and timestamp, to improve performance for 
       similar queries in the future.

### 🦾 Structural Improvements
  1. **Add Indexing:** - Optimize query performance for frequently queried columns.
     - **Query for Indexing:**
       ```bash
       CREATE INDEX idx_zone_timestamp ON plant_readings (zone_id, timestamp);
     - **Outcome:**
        1. Improved Query Performance: Queries filtering by zone_id and timestamp will execute faster, reducing response time for API calls and other database operations.
        2. Efficient Data Access: The index allows the database to locate relevant rows quickly, avoiding costly sequential scans on the plant_readings table.

## 📝 Task 2: REST API

### 📑 Setup for REST API creation

**Run the Application**:
   Start the FastAPI server by running the following command in your project directory:

   ```bash
   uvicorn api.main:app --reload
   ```

   Once the server is running, open your browser and navigate to: **http://127.0.0.1:8000/docs**.
   Use the Swagger UI to test the endpoints.

![image](https://github.com/user-attachments/assets/edc615f3-304c-42fa-a6ba-cecddc75c99e)


### 🔒 Authentication and Security

### JWT Authentication
The project implements **JWT (JSON Web Token)** authentication to secure endpoints and ensure authorized access. The `fastapi-jwt-auth` library is used to handle token creation, validation, and authorization processes. A secret key is set for signing tokens, and an access token is generated during login.

### Secured Endpoints
- All API endpoints, except the `/health-check`, are secured using JWT authentication.
- The `Authorize.jwt_required()` dependency ensures that only requests with valid tokens are allowed access.
- Users must log in via the `/login` endpoint with valid credentials (`admin` and `password` as defaults) to obtain a JWT access token.

### Default Login Credentials for Swagger UI
- Username: admin
- Password: password

### Health Check
The `/health-check` endpoint is publicly accessible and does not require authentication. It is used to verify that the system is operational.

### How It Works:
1. The user provides login credentials to the `/login` endpoint, which returns a JWT access token upon successful authentication.
2. The access token is included in the `Authorization` header (`Bearer <token>`) for all subsequent API requests.
3. Unauthorized requests without a valid token are rejected with a 401 status code.

This setup ensures that the system is both secure and user-friendly, while allowing health monitoring without authentication.

## DATA INGESTION

### 📥 POST /api/v1/sensor-data/batch

### Description
This endpoint allows users to add a batch of sensor data readings for multiple plants in a single API request. The sensor data includes environmental and plant growth metrics such as temperature, humidity, soil moisture, and plant height.

### Request
The request must include a **JWT access token** in the `Authorization` header (`Bearer <token>`).

### Request Body
The request body must be a list of sensor data objects in JSON format. Each object should follow this structure:

```json
[
  {
    "timestamp": "2024-01-01T00:00:00",
    "zone_id": "zone_1",
    "plant_id": "plant_1",
    "temperature": 25.22,
    "humidity": 64.19,
    "soil_moisture": 0.7,
    "light_level": 803.5,
    "plant_height": 10.2,
    "leaf_count": 5
  },
  {
    "timestamp": "2024-01-01T00:05:00",
    "zone_id": "zone_1",
    "plant_id": "plant_2",
    "temperature": 26.10,
    "humidity": 62.00,
    "soil_moisture": 0.8,
    "light_level": 810.0,
    "plant_height": 12.0,
    "leaf_count": 6
  }
]
```

### Response
On success, the API returns a confirmation message:

```json
{
  "message": "Batch sensor data added successfully!"
}
```

![image](https://github.com/user-attachments/assets/711b7aa6-53f3-4caf-bfd1-5cc61f6be3a7)


### Authentication
This endpoint is secured with **JWT authentication**:
- The user must include a valid token in the `Authorization` header.
- Unauthorized requests without a valid token will receive a `401 Unauthorized` response.

### Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **422 Unprocessable Entity**: If the input data does not match the required format.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.


### 📥 POST /api/v1/sensor-data/single

## Description
This endpoint allows users to add a single sensor data reading for a specific plant. The sensor data includes environmental and plant growth metrics such as temperature, humidity, soil moisture, and plant height.

## Request
The request must include a JWT access token in the Authorization header (`Bearer <token>`).

### Request Body
The request body must be a single sensor data object in JSON format. The object should follow this structure:

```json
{
  "timestamp": "2024-01-01T00:00:00",
  "zone_id": "zone_1",
  "plant_id": "plant_1",
  "temperature": 25.22,
  "humidity": 64.19,
  "soil_moisture": 0.7,
  "light_level": 803.5,
  "plant_height": 10.2,
  "leaf_count": 5
}
```

## Response
On success, the API returns a confirmation message:

```json
{
  "message": "Single sensor data added successfully!"
}
```

![image](https://github.com/user-attachments/assets/12f85343-02d2-4b45-9763-4715045b26a1)


## Authentication
This endpoint is secured with JWT authentication:

- The user must include a valid token in the `Authorization` header.
- Unauthorized requests without a valid token will receive a `401 Unauthorized` response.

## Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **422 Unprocessable Entity**: If the input data does not match the required format.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.


### 📥 GET /api/v1/sensor-data/{zone_id}

## Description
This endpoint retrieves all sensor data associated with a specific zone. The data includes environmental metrics such as temperature, humidity, soil moisture, light level, and plant growth metrics like plant height and leaf count.

## Request
The request must include a JWT access token in the Authorization header (Bearer <token>).

### Parameters
- **zone_id** (string, path): The ID of the zone for which data is to be retrieved.

### Request Example
```bash
GET /api/v1/sensor-data/zone_1
Authorization: Bearer <your_jwt_token>
```

## Response
The response contains a list of sensor data entries for the specified zone.

### Response Example
```json
{
  "zone_id": "zone_1",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "zone_id": "zone_1",
      "plant_id": "plant_1",
      "temperature": 25.22,
      "humidity": 64.19,
      "soil_moisture": 0.7,
      "light_level": 803.5,
      "plant_height": 10.2,
      "leaf_count": 5
    },
    {
      "timestamp": "2024-01-01T00:05:00",
      "zone_id": "zone_1",
      "plant_id": "plant_2",
      "temperature": 26.10,
      "humidity": 62.00,
      "soil_moisture": 0.8,
      "light_level": 810.0,
      "plant_height": 12.0,
      "leaf_count": 6
    }
  ]
}
```

![image](https://github.com/user-attachments/assets/3cf2eb07-1412-4d49-a881-6c03a6b181b7)


## Authentication
This endpoint is secured with JWT authentication:
- A valid token must be included in the Authorization header.
- Unauthorized requests without a valid token will receive a 401 Unauthorized response.

## Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **404 Not Found**: If no data is found for the given `zone_id`.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.


### 📥 GET /api/v1/sensor-data/{zone_id}/{plant_name}

## Description
This endpoint retrieves all sensor data associated with a specific zone and plant. The data includes environmental metrics such as temperature, humidity, soil moisture, light level, and plant growth metrics like plant height and leaf count.

## Request
The request must include a JWT access token in the Authorization header (Bearer <token>).

### Parameters
- **zone_id** (string, path): The ID of the zone for which data is to be retrieved.
- **plant_name** (string, path): The name of the plant for which data is to be retrieved.

### Request Example
```bash
GET /api/v1/sensor-data/zone_1/basil
Authorization: Bearer <your_jwt_token>
```

## Response
The response contains a list of sensor data entries for the specified zone and plant.

### Response Example
```json
{
  "zone_id": "zone_1",
  "plant_name": "basil",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "temperature": 25.22,
      "humidity": 64.19,
      "soil_moisture": 0.7,
      "light_level": 803.5,
      "plant_height": 10.2,
      "leaf_count": 5
    },
    {
      "timestamp": "2024-01-01T00:05:00",
      "temperature": 26.10,
      "humidity": 62.00,
      "soil_moisture": 0.8,
      "light_level": 810.0,
      "plant_height": 12.0,
      "leaf_count": 6
    }
  ]
}
```

![image](https://github.com/user-attachments/assets/f3d2c5e3-3cdf-4fe0-bd33-dc42eaf9a932)


## Authentication
This endpoint is secured with JWT authentication:
- A valid token must be included in the Authorization header.
- Unauthorized requests without a valid token will receive a 401 Unauthorized response.

## Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **404 Not Found**: If no data is found for the given `zone_id` and `plant_name`.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.

## ANALYTICS ENDPOINTS

### 📥 GET /api/v1/analytics/growth-rate/{plant_id}

## Description

This API provides growth trends and analyzes the correlation between a plant's growth and environmental factors such as temperature, humidity, and light levels.

## Request
The request must include a JWT access token in the Authorization header (Bearer <token>).

### Parameters
- **plant_id** (string, path): The ID of the plant for which growth analysis is to be retrieved.

### Request Example
```bash
GET /api/v1/analytics/growth-rate/plant_1
Authorization: Bearer <your_jwt_token>
```

### Response Example
```json
{
  "plant_id": "plant_1",
  "growth_trends": [
    1.2, 1.4, 1.6, 1.5, 1.7, 1.3, 1.8
  ],
  "environmental_correlations": {
    "temperature": 0.60312626939662716,
    "humidity": -0.0566449048235577,
    "light_level": 0.05287755886638926
  }
}
```
![image](https://github.com/user-attachments/assets/80e1c0ae-8f6f-4cff-b3ca-4b0fb65e413f)


## Authentication
This endpoint is secured with JWT authentication:
- A valid token must be included in the Authorization header.
- Unauthorized requests without a valid token will receive a 401 Unauthorized response.

## Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **404 Not Found**: If no data is found for the given `plant_id`.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.

### 📥 GET /api/v1/analytics/optimal-conditions/{species_id}

## Description
This endpoint analyzes historical data to determine ideal growing conditions for a specific plant species. For instance, it can indicate that a species like "pepper" grows best within specific ranges of temperature, humidity, and soil moisture.

## Request
The request must include a JWT access token in the Authorization header (Bearer <token>).

### Parameters
- **species_id** (string, path): The ID of the plant species for which optimal conditions are to be retrieved.

### Request Example
```bash
GET /api/v1/analytics/optimal-conditions/pepper
Authorization: Bearer <your_jwt_token>
```

## Response
The response provides the optimal environmental conditions for the specified plant species.

### Response Example
```json
{
  "species_id": "pepper",
  "optimal_conditions": {
    "temperature_range": [21.59, 28.49],
    "humidity_range": [57.87, 71.44],
    "soil_moisture_range": [0.65, 0.8]
  }
}
```
![image](https://github.com/user-attachments/assets/fffacc31-b8e9-4319-b4ac-b20eeeabd12d)


## Authentication
This endpoint is secured with JWT authentication:
- A valid token must be included in the Authorization header.
- Unauthorized requests without a valid token will receive a 401 Unauthorized response.

## Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **404 Not Found**: If no data is found for the given `species_id`.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.

### 📥 GET /api/v1/analytics/yield-prediction/{zone_id}

## Description
This endpoint provides yield predictions for a specific growing zone based on current conditions and historical data. For example, it might predict that a zone will produce a specific yield by a certain timeframe, along with actionable suggestions for optimizing yield through environmental adjustments.

## Request
The request must include a JWT access token in the Authorization header (Bearer <token>).

### Parameters
- **zone_id** (string, path): The ID of the growing zone for which yield predictions are to be retrieved.

### Request Example
```bash
GET /api/v1/analytics/yield-prediction/zone_3
Authorization: Bearer <your_jwt_token>
```
![image](https://github.com/user-attachments/assets/e505c2a8-ea25-4c3e-a8c8-62012165a64b)


## Response
The response contains the predicted yield, timeframe, and suggestions for improving yield.

### Response Example
```json
{
  "zone_id": "zone_3",
  "predicted_yield": 7317.4,
  "prediction_timeframe": "By February 2025",
  "suggestions": "Consider optimizing temperature and humidity for better yield."
}
```

## Authentication
This endpoint is secured with JWT authentication:
- A valid token must be included in the Authorization header.
- Unauthorized requests without a valid token will receive a 401 Unauthorized response.

## Error Handling
- **401 Unauthorized**: If the token is missing or invalid.
- **404 Not Found**: If no data is found for the given `zone_id`.
- **500 Internal Server Error**: If there is a database issue or unexpected error during processing.

## ֎🇦🇮 AI Usage

ChatGPT was used for brainstorming ideas and initial drafts for certain parts of the project, such as:

- Structuring some FastAPI endpoints.
- Suggesting approaches to improve normalization and validation of sensor data.

The AI-generated suggestions were refined, reviewed, and adapted to align with project-specific requirements, including optimization of database queries, error handling, and performance considerations.

All final implementations and decisions, including critical analytics logic and design choices, were made through manual verification and thorough testing to ensure accuracy and reliability.


