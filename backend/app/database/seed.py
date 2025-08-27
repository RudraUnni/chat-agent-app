"""
Database seeding functionality for creating default users and test data.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from app.services.database.chat_service import DatabaseChatService
from app.core.config import get_settings
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)
settings = get_settings()


async def create_default_user(db: AsyncSession) -> User:
    """Create the default test user if it doesn't exist"""
    chat_service = DatabaseChatService(db)
    
    # Check if default user already exists
    existing_user = await chat_service.get_user_by_username(settings.default_user_username)
    if existing_user:
        logger.info(f"Default user '{settings.default_user_username}' already exists")
        return existing_user
    
    # Check if user exists by email
    existing_user = await chat_service.get_user_by_email(settings.default_user_email)
    if existing_user:
        logger.info(f"User with email '{settings.default_user_email}' already exists")
        return existing_user
    
    # Create the default user
    try:
        user = await chat_service.create_user(
            username=settings.default_user_username,
            email=settings.default_user_email
        )
        logger.info(f"✅ Created default user: {user.username} (ID: {user.id})")
        return user
    except DatabaseError as e:
        if e.error_code == "USER_ALREADY_EXISTS":
            # This shouldn't happen due to our checks above, but handle it gracefully
            logger.warning(f"Default user creation skipped - user already exists: {e}")
            # Try to get the user again
            return await chat_service.get_user_by_username(settings.default_user_username)
        else:
            logger.error(f"Failed to create default user: {e}")
            raise


async def seed_database(db: AsyncSession):
    """Seed the database with initial data"""
    if not settings.create_default_user:
        logger.info("Default user creation disabled in configuration")
        return
    
    logger.info("🌱 Seeding database with default user...")
    
    try:
        default_user = await create_default_user(db)
        logger.info(f"🌱 Database seeding completed. Default user ID: {default_user.id}")
        
        # Store the default user ID for easy access (could be used by tests)
        logger.info(f"🔑 Default user credentials: {settings.default_user_username} / {settings.default_user_email}")
        
    except Exception as e:
        logger.error(f"❌ Database seeding failed: {e}")
        raise


async def get_default_user(db: AsyncSession) -> User:
    """Get the default user, creating it if necessary"""
    chat_service = DatabaseChatService(db)
    
    # Try to get by username first
    user = await chat_service.get_user_by_username(settings.default_user_username)
    if user:
        return user
    
    # Try to get by email
    user = await chat_service.get_user_by_email(settings.default_user_email)
    if user:
        return user
    
    # Create if doesn't exist
    logger.info("Default user not found, creating...")
    return await create_default_user(db)