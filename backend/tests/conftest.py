"""
Конфигурация pytest для тестирования API
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from main import app
from auth.dep import get_current_user

# Импортируем все модели
from auth.models import User
from my_tasks.models import Task, TaskAssignment
from rooms.models import Room, RoomMember
from auth.security_service.token_models import RefreshTokenSession, TokenBlacklist

from auth.security_service.password import hash_password


# Тестовая база данных - используем StaticPool для in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Создаем асинхронный движок для тестов"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Создаем тестовую сессию"""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_user(test_db: AsyncSession) -> User:
    """Создаем тестового пользователя"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        is_lead=False
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_lead_user(test_db: AsyncSession) -> User:
    """Создаем тестового пользователя-лида"""
    user = User(
        username="testlead",
        email="lead@example.com",
        hashed_password=hash_password("leadpassword123"),
        is_active=True,
        is_lead=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_user_2(test_db: AsyncSession) -> User:
    """Создаем второго тестового пользователя"""
    user = User(
        username="testuser2",
        email="test2@example.com",
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        is_lead=False
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession, test_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Создаем тестовый HTTP клиент с мокированной аутентификацией"""
    
    async def override_get_db():
        yield test_db
    
    async def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_lead(test_db: AsyncSession, test_lead_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Создаем тестовый HTTP клиент с мокированной аутентификацией для лида"""
    
    async def override_get_db():
        yield test_db
    
    async def override_get_current_user():
        return test_lead_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_unauthorized(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создаем тестовый HTTP клиент без аутентификации"""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
