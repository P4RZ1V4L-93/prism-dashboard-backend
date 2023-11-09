'''
    This Python script includes various components such as authentication using JWT (JSON Web Tokens), routing, middleware for handling CORS (Cross-Origin Resource Sharing), and custom OpenAPI documentation generation
'''

# Importing necessary modules
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from schemas import Settings
from auth_routes import auth_router
from data_routes import data_router
import re
import inspect

# Instantiating the FastAPI app
app = FastAPI()


# Configuring CORS (Cross-Origin Resource Sharing) middleware to allow requests from all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routes defined in auth_router and data_router
app.include_router(auth_router)
app.include_router(data_router)


# Defining a function get_config that loads the configuration from Settings class
@AuthJWT.load_config
def get_config():
    return Settings()

# Defining a custom OpenAPI documentation generator
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Device Classification Dashboard API",
        version="1.0",
        description="This documentation provide end points for Device Classification dashboard.",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        }
    }

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            if (
                re.search("jwt_required", inspect.getsource(endpoint)) or
                re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
                re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {
                        "Bearer Auth": []
                    }
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Assigning the custom OpenAPI function to app.openapi
app.openapi = custom_openapi