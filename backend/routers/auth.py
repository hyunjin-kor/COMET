"""Same-origin browser sessions for opt-in hosted mode."""

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from backend.config import settings
from backend.services import hosted_access as hosted
from backend.services.hosted_subscription import subscription_view

router = APIRouter(prefix="/api/auth", tags=["account"])


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(pattern=r"^[A-Za-z0-9._@+-]{3,128}$")
    password: SecretStr = Field(min_length=1, max_length=128)


class AccountView(BaseModel):
    id: str
    username: str
    organization_id: str
    subscription: dict


class SessionView(BaseModel):
    mode: str
    authenticated: bool
    account: AccountView | None = None


def _session_view(account=None):
    return SessionView(mode="hosted" if settings.hosted_mode else "desktop", authenticated=account is not None,
                       account=AccountView(id=account.id, username=account.username, organization_id=account.organization_id,
                                           subscription=subscription_view(account.organization_id)) if account else None)


@router.get("/session", response_model=SessionView)
def current_session(request: Request):
    return _session_view(hosted.account_for_request(request) if settings.hosted_mode else None)


@router.post("/login", response_model=SessionView)
def login(payload: LoginRequest, request: Request, response: Response):
    if not settings.hosted_mode:
        raise HTTPException(404, "Hosted accounts are disabled")
    account, token = hosted.sign_in(payload.username, payload.password.get_secret_value(),
                                    request.client.host if request.client else "unknown",
                                    request.cookies.get(hosted.cookie_name()))
    response.set_cookie(hosted.cookie_name(), token, max_age=hosted.SESSION_SECONDS, path="/", httponly=True,
                        secure=settings.hosted_origin.startswith("https:"), samesite="strict")
    return _session_view(account)


@router.post("/logout")
def logout(request: Request, response: Response):
    if not settings.hosted_mode:
        raise HTTPException(404, "Hosted accounts are disabled")
    hosted.sign_out(request)
    response.delete_cookie(hosted.cookie_name(), path="/", httponly=True,
                           secure=settings.hosted_origin.startswith("https:"), samesite="strict")
    return {"status": "signed_out"}


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: SecretStr = Field(min_length=1, max_length=128)
    new_password: SecretStr = Field(min_length=15, max_length=128)


@router.post("/password")
def change_password(payload: PasswordChangeRequest, request: Request, response: Response):
    if not settings.hosted_mode:
        raise HTTPException(404, "Hosted accounts are disabled")
    hosted.change_password(request.state.hosted_account.id, payload.current_password.get_secret_value(),
                           payload.new_password.get_secret_value(), request.client.host if request.client else "unknown")
    response.delete_cookie(hosted.cookie_name(), path="/", httponly=True,
                           secure=settings.hosted_origin.startswith("https:"), samesite="strict")
    return {"status": "password_changed_sign_in_again"}
