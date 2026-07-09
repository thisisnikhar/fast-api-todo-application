from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Step 1: Define SQLALCHEMY DATABASE URL
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db' # Location of the database on FastAPI application
# %40123 is used to escape @

# Step 2: Create Database Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# check_same_thread allows SQLALCHEMY to check for multiple threads for connection

# Step 3: Create Session Local
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
# Binding the session to the engine that we created

# Step 4: Create Database object
Base = declarative_base()
# When we call database.py file, we will create an object of database, which will be able to control database

