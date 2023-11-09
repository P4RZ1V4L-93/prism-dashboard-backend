'''
    This script provides object relational model to create tables in the database
'''

from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Float

# Define a User class that inherits from the Base class


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(String(), nullable=False)

    def __repr__(self):
        """
        Returns a string representation of a User object.

        Example:
        <User username>
        """
        return f"<User {self.username}>"

# Create a base class for ORM models related to power consumption


class PowerConsumption(Base):

    """
    Abstract base class for power consumption models.

    Attributes:
        id (int): Primary key for the table.
        timestamp (DateTime): Date and time of the power consumption record.
        power (Float): Power consumption value.
        category (String): Category of the power-consuming device.
    """

    __abstract__ = True
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    power = Column(Float, nullable=False)
    category = Column(String, nullable=False)


# Define a dictionary to store category classes
category_classes = {}

# Define a list of categories
categories = ['printer3d', 'airconditioner', 'airpurifier', 'boiler', 'coffee', 'computer', 'dehumidifier', 'dishwasher', 'dryer', 'fan', 'freezer', 'fridge',
              'internetrouter', 'laptop', 'microwaveoven', 'phonecharger', 'printer', 'radiator', 'screen', 'solarpanel', 'soundsystem', 'tv', 'vacuumcleaner', 'washingmachine']

# Iterate through the categories and dynamically create classes and tables
for category in categories:
    class_name = f"{category.replace(' ', '')}PowerConsumption"
    table_name = f"{category.replace(' ', '').lower()}_power_consumption"

    # Define a new class for each category
    exec(f'''
class {class_name}(PowerConsumption):
    __tablename__ = "{table_name}"

category_classes["{category}"] = {class_name}
    
''')
