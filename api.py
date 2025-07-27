from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="Products API", description="API for retrieving products from MySQL database")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'database': os.getenv('DB_NAME', 'products_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {err}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Products API is running", "endpoints": ["/products"]}

@app.get("/products", response_model=List[Dict[str, Any]])
async def get_all_products():
    """Get all products from the products table"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to get all products
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return products
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        connection = get_db_connection()
        connection.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=4500, reload=True) 