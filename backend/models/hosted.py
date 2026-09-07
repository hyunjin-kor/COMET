"""Control records for the optional hosted service, separate from user data."""

from uuid import uuid4

from sqlmodel import Field, SQLModel


class HostedOrganization(SQLModel, table=True):
    __tablename__ = "hosted_organizations"
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    name: str


class HostedAccount(SQLModel, table=True):
    __tablename__ = "hosted_accounts"
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    organization_id: str = Field(index=True)
    username: str = Field(unique=True, index=True)
    password_hash: str = Field(repr=False)
    enabled: bool = True


class HostedLoginSession(SQLModel, table=True):
    __tablename__ = "hosted_login_sessions"
    token_hash: str = Field(primary_key=True, repr=False)
    account_id: str = Field(index=True)
    expires_at: float


class HostedLoginThrottle(SQLModel, table=True):
    __tablename__ = "hosted_login_throttle"
    key: str = Field(primary_key=True)
    window: int
    attempts: int = 0
