import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.database import init_db
from main import app

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initializes database tables on test session start."""
    await init_db()

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
