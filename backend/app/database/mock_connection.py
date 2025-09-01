
import asyncio
from typing import Optional

# Mock database connection
class MockDatabase:
    def __init__(self):
        self.connected = True
    
    async def connect(self):
        self.connected = True
        return True
    
    async def disconnect(self):
        self.connected = False
    
    def is_healthy(self):
        return self.connected

# Global mock database instance
mock_db = MockDatabase()

async def init_db():
    """Initialize mock database"""
    await mock_db.connect()
    print("✅ Mock database initialized")

async def close_db():
    """Close mock database"""
    await mock_db.disconnect()
    print("✅ Mock database closed")

def get_db():
    """Get database connection"""
    return mock_db
