# Amazon Crawler with Separate Containers

This project consists of two main services:
1. **API Service** (`api.py`) - FastAPI service for retrieving products from the database
2. **Crawler Service** (`main.py`) - Web crawler that scrapes Amazon products

## Architecture

- **MySQL Database** - Stores the scraped product data
- **API Container** - Serves the FastAPI application on port 4500
- **Crawler Container** - Runs the Amazon product crawler
- **Docker Network** - All containers communicate through a shared network

## Quick Start

1. **Build and run all services:**
   ```bash
   docker-compose up --build
   ```

2. **Run services in background:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f api
   docker-compose logs -f crawler
   docker-compose logs -f mysql
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

## Individual Container Management

### API Service
```bash
# Build API container only
docker build -f Dockerfile.api -t products-api .

# Run API container
docker run -p 4500:4500 --network crawler_network --env-file .env products-api
```

### Crawler Service
```bash
# Build crawler container only
docker build -f Dockerfile.main -t products-crawler .

# Run crawler container
docker run --network crawler_network --env-file .env products-crawler
```

## API Endpoints

Once the API service is running, you can access:

- **Health Check:** `GET http://localhost:4500/health`
- **All Products:** `GET http://localhost:4500/products`
- **Root:** `GET http://localhost:4500/`

## Environment Variables

The following environment variables can be configured:

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 3306)
- `DB_USER` - Database user (default: root)
- `DB_PASSWORD` - Database password (default: 12345678)
- `DB_NAME` - Database name (default: products_db)

## Database

The MySQL database will be automatically created with the `products_db` database and the `products` table will be created by the crawler service. The database is accessible on port **3307** (mapped from container port 3306).

## Troubleshooting

1. **Database connection issues:** Ensure MySQL container is running and healthy
2. **Crawler not working:** Check if Playwright browsers are properly installed
3. **API not accessible:** Verify the API container is running and port 4500 is exposed

## Development

For local development without Docker:

1. Install dependencies: `pip install -r requirements.txt`
2. Install Playwright browsers: `playwright install firefox`
3. Start MySQL database
4. Run API: `python api.py`
5. Run crawler: `python main.py` 