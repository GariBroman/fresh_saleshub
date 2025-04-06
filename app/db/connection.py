import logging
import asyncpg
import os
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection string from environment variables
DB_URL = os.getenv("DATABASE_URL", "")

# Global connection pool
pool = None

async def init_db():
    """Initialize database connection pool"""
    global pool
    
    if not DB_URL:
        logging.error("DATABASE_URL not set in environment variables")
        return None
    
    logging.info(f"Connecting to database with URL: {DB_URL[:20]}[...]")
        
    try:
        pool = await asyncpg.create_pool(DB_URL)
        if pool:
            logging.info("Database connection pool created successfully")
            await create_tables()
            # Test the connection
            async with pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logging.info(f"Connected to database: {version}")
            return pool
        else:
            logging.error("Failed to create database pool (pool is None)")
            return None
    except asyncpg.exceptions.InvalidPasswordError:
        logging.error("Database connection failed: Invalid password")
        return None
    except asyncpg.exceptions.InvalidCatalogNameError:
        logging.error("Database connection failed: Database does not exist")
        return None
    except asyncpg.exceptions.ConnectionDoesNotExistError:
        logging.error("Database connection failed: Connection does not exist")
        return None
    except Exception as e:
        logging.error(f"Error creating database connection pool: {e}")
        logging.error(traceback.format_exc())
        return None

async def close_db():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        logging.info("Database connection pool closed")
    else:
        logging.warning("No database pool to close")

async def create_tables():
    """Create required tables if they don't exist"""
    global pool
    if not pool:
        logging.error("Database pool not initialized")
        return

    try:
        async with pool.acquire() as conn:
            # Create users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    chat_id BIGINT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    UNIQUE(user_id)
                )
            ''')
            
            # Check if the table was created
            table_exists = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
            )
            if table_exists:
                logging.info("Database tables created/verified successfully")
            else:
                logging.error("Failed to create users table")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")
        logging.error(traceback.format_exc()) 