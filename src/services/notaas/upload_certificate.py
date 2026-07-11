import secrets
from datetime import datetime, timedelta, timezone
from src.managers.tokens_manager import TokensManager

def gen_upload_token(prestador_id: int, ttl_min: int = 15) -> str:

    token = secrets.token_urlsafe(32)
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_min)

    TokensManager().insert_token(token, prestador_id, expire_at)
    return token

def expirado(expire_at: str | datetime) -> bool:
    if isinstance(expire_at, str):
        expire_at = datetime.fromisoformat(expire_at)

    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=timezone.utc)
        
    return datetime.now(timezone.utc) > expire_at