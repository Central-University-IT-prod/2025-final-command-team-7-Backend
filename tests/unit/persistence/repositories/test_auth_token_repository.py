import datetime
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import AuthTokenNotFoundError
from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.auth_token import auth_token_to_orm
from backend.infrastructure.persistence.models.auth_token import AuthTokenORM
from backend.infrastructure.persistence.repositories.auth_token import SQLAlchemyAuthTokenRepository


class TestSQLAlchemyAuthTokenRepository:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token="test_token",
            user_id=user_id,
            activated=True,
            declined=False,
            created_at=created_at
        )
        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        created_token = await repo.create(auth_token)

        
        assert created_token.id == auth_token_id
        assert created_token.token == "test_token"
        assert created_token.user_id == user_id
        assert created_token.activated is True
        assert created_token.declined is False
        assert created_token.created_at == created_at

        
        result = await db_session.execute(select(AuthTokenORM).where(AuthTokenORM.id == auth_token_id))
        db_token = result.scalars().first()
        assert db_token is not None
        assert db_token.token == "test_token"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token="test_token",
            user_id=user_id,
            activated=True,
            declined=False,
            created_at=created_at
        )
        orm_token = auth_token_to_orm(auth_token)
        db_session.add(orm_token)
        await db_session.commit()

        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        retrieved_token = await repo.get_by_id(auth_token_id)

        
        assert retrieved_token.id == auth_token_id
        assert retrieved_token.token == "test_token"
        assert retrieved_token.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        with pytest.raises(AuthTokenNotFoundError):
            await repo.get_by_id(auth_token_id)

    @pytest.mark.asyncio
    async def test_get_by_token_found(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        token_str = "test_token_123"
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token=token_str,
            user_id=user_id,
            activated=True,
            declined=False,
            created_at=created_at
        )
        orm_token = auth_token_to_orm(auth_token)
        db_session.add(orm_token)
        await db_session.commit()

        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        retrieved_token = await repo.get_by_token(token_str)

        
        assert retrieved_token.id == auth_token_id
        assert retrieved_token.token == token_str
        assert retrieved_token.user_id == user_id

    @pytest.mark.asyncio
    async def test_get_by_token_not_found(self, db_session: AsyncSession):
        
        token_str = "nonexistent_token"
        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        with pytest.raises(AuthTokenNotFoundError):
            await repo.get_by_token(token_str)

    @pytest.mark.asyncio
    async def test_update(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token="test_token",
            user_id=user_id,
            activated=False,
            declined=False,
            created_at=created_at
        )
        orm_token = auth_token_to_orm(auth_token)
        db_session.add(orm_token)
        await db_session.commit()

        
        updated_token = AuthToken(
            id=auth_token_id,
            token="test_token",
            user_id=user_id,
            activated=True,
            declined=False,
            created_at=created_at
        )

        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        result = await repo.update(updated_token)

        
        assert result.activated is True

        
        result = await db_session.execute(select(AuthTokenORM).where(AuthTokenORM.id == auth_token_id))
        db_token = result.scalars().first()
        assert db_token is not None
        assert db_token.activated is True

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token="test_token",
            user_id=user_id,
            activated=True,
            declined=False,
            created_at=created_at
        )

        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        with pytest.raises(AuthTokenNotFoundError):
            await repo.update(auth_token)

    @pytest.mark.asyncio
    async def test_activate_token(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        token_str = "test_token_123"
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token=token_str,
            user_id=None,
            activated=False,
            declined=False,
            created_at=created_at
        )
        orm_token = auth_token_to_orm(auth_token)
        db_session.add(orm_token)
        await db_session.commit()

        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        result = await repo.activate_token(token_str, user_id)

        
        assert result.activated is True
        assert result.user_id == user_id

        
        result = await db_session.execute(select(AuthTokenORM).where(AuthTokenORM.token == token_str))
        db_token = result.scalars().first()
        assert db_token is not None
        assert db_token.activated is True
        assert db_token.user_id == user_id

    @pytest.mark.asyncio
    async def test_decline_token(self, db_session: AsyncSession):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        token_str = "test_token_123"
        created_at = datetime.datetime.now(datetime.UTC)

        auth_token = AuthToken(
            id=auth_token_id,
            token=token_str,
            user_id=None,
            activated=False,
            declined=False,
            created_at=created_at
        )
        orm_token = auth_token_to_orm(auth_token)
        db_session.add(orm_token)
        await db_session.commit()

        repo = SQLAlchemyAuthTokenRepository(session=db_session)

        
        result = await repo.decline_token(token_str)

        
        assert result.declined is True

        
        result = await db_session.execute(select(AuthTokenORM).where(AuthTokenORM.token == token_str))
        db_token = result.scalars().first()
        assert db_token is not None
        assert db_token.declined is True