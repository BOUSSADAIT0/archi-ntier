import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_config() -> Dict[str, Any]:
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3309')),
        'user': os.getenv('DB_USER', 'app_user'),
        'password': os.getenv('DB_PASSWORD', 'app_password'),
        'database': os.getenv('DB_NAME', 'event_booking')
    }

def init_database_pool():
    """Initialize the database connection pool."""
    from ..persistence.connection_pool import DatabaseConnectionPool
    
    config = get_database_config()
    return DatabaseConnectionPool.get_instance(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database'],
        pool_size=5
    ) 