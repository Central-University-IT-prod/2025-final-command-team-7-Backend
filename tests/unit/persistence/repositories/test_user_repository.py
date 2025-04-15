import uuid

import pytest
from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import UserNotFoundError
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.user import user_to_orm
from backend.infrastructure.persistence.models.user import UserORM
from backend.infrastructure.persistence.repositories.user import SQLAlchemyUserRepository


class TestSQLAlchemyUserRepository:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        
        user_id = UserId(uuid.uuid4())
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )
        repo = SQLAlchemyUserRepository(session=db_session)

        
        created_user = await repo.create(user)

        
        assert created_user.id == user_id
        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"
        assert created_user.hashed_password == "hashedpassword123"
        assert created_user.telegram_id is None

        
        result = await db_session.execute(select(UserORM).where(UserORM.id == user_id))
        db_user = result.scalars().first()
        assert db_user is not None
        assert db_user.username == "testuser"
        assert db_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        
        user_id = UserId(uuid.uuid4())
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )
        orm_user = user_to_orm(user)
        db_session.add(orm_user)
        await db_session.commit()

        repo = SQLAlchemyUserRepository(session=db_session)

        
        retrieved_user = await repo.get_by_id(user_id)

        
        assert retrieved_user.id == user_id
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        
        user_id = UserId(uuid.uuid4())
        repo = SQLAlchemyUserRepository(session=db_session)

        
        with pytest.raises(UserNotFoundError):
            await repo.get_by_id(user_id)

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, db_session: AsyncSession):
        
        user_id = UserId(uuid.uuid4())
        email = "test@example.com"
        user = User(
            id=user_id,
            username="testuser",
            email=email,
            hashed_password="hashedpassword123",
            telegram_id=None
        )
        orm_user = user_to_orm(user)
        db_session.add(orm_user)
        await db_session.commit()

        repo = SQLAlchemyUserRepository(session=db_session)

        
        retrieved_user = await repo.get_by_email(email)

        
        assert retrieved_user.id == user_id
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == email

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, db_session: AsyncSession):
        
        email = "nonexistent@example.com"
        repo = SQLAlchemyUserRepository(session=db_session)

        
        with pytest.raises(UserNotFoundError):
            await repo.get_by_email(email)

    @pytest.mark.asyncio
    async def test_update(self, db_session: AsyncSession):
        
        user_id = UserId(uuid.uuid4())
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )
        orm_user = user_to_orm(user)
        db_session.add(orm_user)
        await db_session.commit()

        
        updated_user = User(
            id=user_id,
            username="updateduser",
            email="updated@example.com",
            hashed_password="updatedhashed123",
            telegram_id=12345
        )

        repo = SQLAlchemyUserRepository(session=db_session)

        
        result = await repo.update(updated_user)

        
        assert result.username == "updateduser"
        assert result.email == "updated@example.com"
        assert result.hashed_password == "updatedhashed123"
        assert result.telegram_id == 12345

        
        result = await db_session.execute(select(UserORM).where(UserORM.id == user_id))
        db_user = result.scalars().first()
        assert db_user is not None
        assert db_user.username == "updateduser"
        assert db_user.email == "updated@example.com"

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session: AsyncSession):
        
        user_id = UserId(uuid.uuid4())
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )

        repo = SQLAlchemyUserRepository(session=db_session)

        
        with pytest.raises(UserNotFoundError):
            await repo.update(user)