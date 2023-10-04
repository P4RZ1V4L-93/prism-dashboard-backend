'''
    This script is indexing the power column in each of the tables associated with the different device categories
'''

# import necessary dependencies
from sqlalchemy import Index
from models import categories, category_classes
from database import engine

# index all the power column of distinct devices' table
for category in categories:
    category_class = category_classes[category]    
    index_name = f'idx_power_{category}'
    column = getattr(category_class, 'power')
    index = Index(index_name, column)
    index.create(bind=engine)



