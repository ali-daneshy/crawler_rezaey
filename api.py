from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from typing import List, Dict, Any, Optional
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
    return {"message": "Products API is running", "endpoints": ["/products", "/products/paginated"]}

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

@app.get("/products/paginated")
async def get_products_paginated(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)")
):
    """Get products with pagination"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count of products
        cursor.execute("SELECT COUNT(*) as total FROM products")
        total_count = cursor.fetchone()['total']
        
        # Get paginated products
        cursor.execute("SELECT * FROM products LIMIT %s OFFSET %s", (page_size, offset))
        products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        return {
            "data": products,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
                "next_page": page + 1 if has_next else None,
                "previous_page": page - 1 if has_previous else None
            }
        }
        
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