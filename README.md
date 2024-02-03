# OpenWeather API

## Overview

The Weather API provides weather reports for any country in three languages: English, German, and Bengali. It sources its data from [Open Weather](https://openweathermap.org).

## Weather API - Local Development Setup

This guide provides instructions for setting up and running the Weather API locally using Docker Compose.

### Prerequisites

Make sure you have the following installed on your local machine:

- [Docker >= 24.0](https://www.docker.com/get-started)
- [Docker Compose >= 2.21.0](https://docs.docker.com/compose/install/)

### Steps

1. **Clone the Repository**

   ```bash
   git clone git@github.com:mohidex/openweather-api.git
   cd openweather-api
   ```

2. **Docker Compose Configuration**

    Customize the following environment variables for the 'web' service:
      ```yaml
      - SECRET_KEY=<django-secret-key>
      - MIGRATE_ON_STARTUP=True
      - OPEN_WEATHER_API_KEY=<your-api-key>
      - CACHE_TIMEOUT_IN_MIN=<cached-timeout> # could be 5, 10, 60
    ```
3. **Build and Run the Containers**

   Execute the following command to build and run the Docker containers:

   ```bash
   docker compose up --build
   ```

   This command will pull the necessary images, build the application, and start the development server.

4. **Access the API**

   Once the containers are running, you can access the Weather API at [http://localhost:8000/api/v1/weather](http://localhost:8000/api/v1/weather).

5. **Access Swagger Documentation**

   Explore the API using the Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs) to test different endpoints and view the API specifications.

6. **Stopping the Containers**

   To stop the containers, press `Ctrl + C` in the terminal where the `docker compose up` command is running.

   If you want to stop and remove the containers, use the following command:

   ```bash
   docker compose down
   ```


## API Documentation

### Endpoint: `/api/v1/weather`

#### Method: `GET`

##### Parameters

- `city` (Query Parameter): The name of the city for which you want to get the weather report.
  - Type: String
  - Required: Yes

- `Accept-Language` (Header Parameter): The preferred language for the response.
  - Type: String
  - Enum: en-us, de, bn
  - Default: en-us

##### Responses

- `200` (Successful Response)
  - Content Type: `application/json`
  - Example:
    ```json
    {
      "status": "success",
      "data": {
        "city": "Dhaka",
        "temperature": {
          "current": 16.99,
          "minimum": 16.99,
          "maximum": 16.99
        },
        "humidity": 59,
        "pressure": 1017,
        "wind": {
          "speed": 0,
          "direction": "North"
        },
        "description": "haze"
      }
    }
    ```

- `400` (Bad Request)
  - Content Type: `application/json`
  - Example:
    ```json
    {
      "status": "error",
      "message": "Bad Request: No city provided."
    }
    ```

- `404` (Not Found)
  - Content Type: `application/json`
  - Example:
    ```json
    {
      "status": "error",
      "message": "Not Found: No city found with the provided query."
    }
    ```

- `503` (Service Unavailable)
  - Content Type: `application/json`
  - Example:
    ```json
    {
      "status": "error",
      "message": "Service Unavailable: The service is currently unavailable. Please try again later."
    }
    ```

## Contact
For any inquiries, please contact: [mohidul.cs@gmail.com](mailto:mohidul.cs@gmail.com)

## License
This project is licensed under the [MIT License](https://www.mit.edu/~amini/LICENSE.md).