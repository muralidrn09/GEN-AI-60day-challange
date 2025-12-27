from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _truncate_password(password: str) -> str:
    """Truncate password to 72 bytes (bcrypt limitation)."""
    return password.encode('utf-8')[:72].decode('utf-8', errors='ignore')


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(_truncate_password(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(_truncate_password(plain_password), hashed_password)
