# auth/token_utils.py
import os
from typing import Optional, Dict, Any

import jwt           # pip install PyJWT
from jwt import PyJWTError

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
ALGORITHM = os.getenv("JWT_ALG", "HS256")          # HS256 (dev) or RS256 (prod)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret") # used only for HS256
JWT_PUBKEY = os.getenv("JWT_PUBKEY",  "")          # PEM for RS256

# Optional audience / issuer checks
JWT_AUDIENCE = os.getenv("JWT_AUD", None)
JWT_ISSUER   = os.getenv("JWT_ISS", None)


# ------------------------------------------------------------------
# Public helpers
# ------------------------------------------------------------------
def decode_oauth_token(token: str) -> Optional[str]:
    """
    Validate the JWT and return agent_id (sub claim) or None if invalid.
    """
    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            key=_select_key(),
            algorithms=[ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={
                "require": ["sub", "exp"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": bool(JWT_AUDIENCE),
                "verify_iss": bool(JWT_ISSUER),
            },
        )
        return payload.get("sub")          # our agent_id
    except PyJWTError as err:
        print(f"JWT validation error: {err}")
        return None


# ------------------------------------------------------------------
# Internal
# ------------------------------------------------------------------
def _select_key():
    if ALGORITHM.startswith("HS"):
        return JWT_SECRET
    else:  # RS256 / ES256 etc.
        if not JWT_PUBKEY:
            raise RuntimeError("JWT_PUBKEY environment variable not set for RS/ES algorithms")
        return JWT_PUBKEY
