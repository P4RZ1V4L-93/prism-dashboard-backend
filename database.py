'''
    This Python script sets up the database connection and configuration using SQLAlchemy
'''

# import necessary dependencies
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

# Creating the Database Engine
engine=create_engine('postgresql://postgres:postgre@localhost/prism_dashboard',
    echo=True
)

# Creating a Declarative Base
Base=declarative_base()
# Creating a Session Class
Session=sessionmaker()