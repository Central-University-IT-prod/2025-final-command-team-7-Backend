import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.infrastructure.persistence.committer import SQLAlchemyCommitter


class TestSQLAlchemyCommitter:
    @pytest.mark.asyncio
    async def test_commit(self):
        
        mock_session = AsyncMock()
        committer = SQLAlchemyCommitter(session=mock_session)

        
        await committer.commit()

        
        mock_session.commit.assert_called_once()