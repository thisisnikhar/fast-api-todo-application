# Step 1: Import Declarative Base
from .database import Base
# Step 3: Import Column and Integer
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


# Step 5: Creating Users class
class Users(Base):
    # Defining table name
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String,unique=True)
    username = Column(String,unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean,default=True)
    role = Column(String)
    phone_number = Column(String) # Adding the column


# Step 2: Defining Model Class
class Todos(Base):
    # Defining table name
    __tablename__ = "todos"

    # Step 4: Defining the columns of the table
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey(Users.id)) # Step 6: References Users.id as foreign Key

