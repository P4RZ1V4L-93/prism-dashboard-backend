'''
    This script provides validation, response and configuration schema for requesting data
'''

# Import necessary dependencies
from pydantic import BaseModel
from datetime import datetime

# Signup Schema to validate signup request
class SignUpSchema(BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "john123",
                "email": "john@gmail.com",
                "password": "john123@"
            }
        }

# Login Schema to validate login request
class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            'example': {
                "email": "john@gamil.com",
                "password": "john123@",
            }
        }

# Power Consumption schema to validate data point
class PowerConsumptionSchema(BaseModel):
    timestamp: datetime
    power: float
    category: str

    class Config:
        schema_extra = {
            'example': {
                "timestamp": "2020-12-01 06:57:48+00:00",
                "power": 7.2,
                "category": "printer3d"
            }
        }

# Define schema for Response in form of message
class ResponseSchema(BaseModel):
    message: str

    class Config:
        schema_extra = {
            'example': {
                "message": "string"
            }
        }

# Define schema for SignUp Response
class SignUpResponseSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        schema_extra = {
            'example': {
                "id": 1,
                "username": "john",
                "email": "john123@gmail.com"
            }
        }

# Define schema for Login Response
class LoginResponseSchema(BaseModel):
    accessToken: str

    class Config:
        schema_extra = {
            'example': {
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            }
        }

# Define schema for Error Response
class ErrorResonseSchema(BaseModel):
    detail: str

    class Confit:
        schema_extra = {
            "example": {
                "detail": "message"
            }
        }

# Define schema for Statistics data as a Response
class StatisticsResonseSchema(BaseModel):
    count: float
    mean: float
    std: float
    min: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    max: float
    median: float

    class Config:
        schema_extra = {
            "example": {

                "count": 457.00,
                "mean": 44.00,
                "std": 4.00,
                "min": 0.00,
                "percentile_25": 457.00,
                "percentile_50": 457.00,
                "percentile_75": 457.00,
                "max": 45.00,
                "median": 4.30,
            }
        }

# Schema used to configure the secret key for usage of JWT
class Settings(BaseModel):
    authjwt_secret_key: str = 'eb642a0ebaf6500e0fc17a7a3e076413d2e2e993a549b8020f683dd9167fb938'
