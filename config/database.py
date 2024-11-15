import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL="postgresql://nurenai:Biz1nurenWar*@nurenaistore.postgres.database.azure.com/nurenpostgres_Whatsapp"

# Get the database URL from the environment variables
DATABASE_URL = DATABASE_URL

# Set up SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a base class for the models
Base = declarative_base()

# Dependency function for using sessions in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
