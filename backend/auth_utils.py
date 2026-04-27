import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from jose import JWTError, jwt
import bcrypt

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-change-it-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

RP_NAME = "Vision-Mamba Deepfake Detector"
RP_ID = "localhost"
ORIGIN = "http://localhost:3000"

# ─── Password helpers ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        print(f"PASSWORD VERIFY ERROR: {e}")
        return False

# ─── JWT helpers ─────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    from datetime import timezone
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ─── WebAuthn helpers ─────────────────────────────────────────────────────────

def get_registration_options(username: str, user_id: str, existing_credentials: List[Dict] = None):
    from webauthn import generate_registration_options
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        UserVerificationRequirement,
        AuthenticatorAttachment,
        PublicKeyCredentialDescriptor,
    )

    if existing_credentials is None:
        existing_credentials = []

    # Build exclude list so the same device can't register twice
    exclude = []
    for cred in existing_credentials:
        try:
            exclude.append(
                PublicKeyCredentialDescriptor(id=bytes.fromhex(cred["credential_id"]))
            )
        except Exception:
            pass  # skip malformed credential ids

    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=user_id.encode("utf-8"),   # must be bytes
        user_name=username,
        user_display_name=username,
        exclude_credentials=exclude,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    return options


def get_authentication_options(existing_credentials: List[Dict]):
    from webauthn import generate_authentication_options
    from webauthn.helpers.structs import (
        UserVerificationRequirement,
        PublicKeyCredentialDescriptor,
    )

    allow = []
    for cred in existing_credentials:
        try:
            allow.append(
                PublicKeyCredentialDescriptor(id=bytes.fromhex(cred["credential_id"]))
            )
        except Exception:
            pass

    options = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=allow,
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    return options


def do_verify_registration(credential_response: dict, expected_challenge: bytes):
    from webauthn import verify_registration_response
    from webauthn.helpers.structs import RegistrationCredential

    return verify_registration_response(
        credential=credential_response,
        expected_challenge=expected_challenge,
        expected_origin=ORIGIN,
        expected_rp_id=RP_ID,
    )


def do_verify_authentication(
    credential_response: dict,
    expected_challenge: bytes,
    public_key: bytes,
    sign_count: int,
):
    from webauthn import verify_authentication_response

    return verify_authentication_response(
        credential=credential_response,
        expected_challenge=expected_challenge,
        expected_rp_id=RP_ID,
        expected_origin=ORIGIN,
        credential_public_key=public_key,
        credential_current_sign_count=sign_count,
    )
