from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite connection string for local debugging (no Docker)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'products_db.sqlite3')}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Define Product model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_url = Column(String(1024), unique=True, index=True)
    link_of_product = Column(Text)
    title = Column(Text)
    real_price = Column(Integer)
    discounted_price = Column(Integer)
    discount_percentage = Column(Integer)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 