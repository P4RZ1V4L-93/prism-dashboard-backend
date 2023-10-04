# FastAPI Backend for Power Data Analysis

This FastAPI backend is designed to perform power data analysis of various appliances. It provides endpoints for user authentication, data retrieval, and statistical analysis. The backend interfaces with a database and Redis for data storage and caching.

## Features

- User registration and login
- Data retrieval endpoints for statistics and plots
- Database integration for storing power consumption data
- Redis caching for optimized data retrieval
- Basic error handling and response schemas

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/creatorGod003/prism-dashboard-backend.git

2. **Install Dependencies**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate
    pip install -r requirements.txt

3. **Database Configuration**
    
    Set up your PostgreSQL database and update the connection string in database.py

4. **Redis Configuration**

    Install and configure a Redis server, and update the connection details in the relevant files.

5. **Run the Application**

    ```bash
    uvicorn main:app --reload


The API will be accessible at http://localhost:8000

## API Endpoints

* POST /auth/signup: Register a new user.
* POST /auth/login: Log in an existing user.
* GET /data/statistics/{category_name}: Get statistics for a specific device category.
* GET /data/plot/{category_name}: Get a plot for a specific device category.
* POST /data/add: Add power consumption data for a specific device category.
* GET /docs: To see the api documentation

## Backend Architecture

[Link to Backend Architecture](https://tinyurl.com/mah7nedd)

## Contributing
1. Fork the repository
2. Create a new branch (git checkout -b feature)
3. Make your changes and commit them (git commit -m 'Add feature')
4. Push to the branch (git push origin feature)
5. Create a pull request

## License
This project is license under [MIT](https://github.com/creatorGod003/prism-dashboard-backend/blob/main/LICENSE) 

## Acknowledgments

* [FastAPI Documentation](https://fastapi.tiangolo.com/)
* [Redis Documentation](https://redis.io/docs/) 
* [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/)


