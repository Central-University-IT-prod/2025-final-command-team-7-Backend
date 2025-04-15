import dataclasses
import datetime

from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user_id import UserId


@dataclasses.dataclass
class AuthToken:
    id: AuthTokenId
    token: str
    user_id: UserId | None
    activated: bool
    declined: bool
    created_at: datetime.datetime
