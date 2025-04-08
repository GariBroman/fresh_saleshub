import logging
import traceback
from datetime import datetime
from .connection import pool

async def log_user(user_id, username, first_name, last_name, chat_id):
    """
    Log user information to database
    
    Returns:
        tuple: (success, is_new_user) - success indicates if logging was successful,
               is_new_user indicates if this user was newly added to the database
    """
    if not user_id:
        logging.warning("Cannot log user: user_id is None or empty")
        return False, False
        
    if not pool:
        logging.error("Database pool not initialized - cannot log user")
        return False, False
    
    try:
        async with pool.acquire() as conn:
            # Debug logging
            logging.debug(f"Logging user: {user_id}, username: {username}, chat_id: {chat_id}")
            
            # Check if user already exists
            existing_user = await conn.fetchrow(
                'SELECT id FROM users WHERE user_id = $1', user_id
            )
            
            is_new_user = False
            
            if not existing_user:
                # Insert new user
                await conn.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name, chat_id, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''', user_id, username, first_name, last_name, chat_id, datetime.now())
                logging.info(f"New user logged: {user_id} ({username or 'no username'})")
                
                # Verify the user was inserted
                verify = await conn.fetchrow('SELECT id FROM users WHERE user_id = $1', user_id)
                if verify:
                    logging.info(f"User insertion verified: {user_id}")
                    is_new_user = True
                else:
                    logging.error(f"User insertion failed: {user_id}")
            else:
                logging.info(f"User already exists: {user_id} ({username or 'no username'})")
            
            return True, is_new_user
    except Exception as e:
        logging.error(f"Error logging user: {e}")
        logging.error(traceback.format_exc())
        return False, False 