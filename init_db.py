'''
    This Python script is responsible for creating database tables based on the models defined
'''

# Import necessary modules
from database import engine,Base

# Table creation
Base.metadata.create_all(bind=engine)