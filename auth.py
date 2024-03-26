import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from models import User
from sqlalchemy.orm import Session

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    """Verify if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create an access token using JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate the user using the provided username and password."""
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False, "User not found"
        if not verify_password(password, user.password):
            return False, "Invalid password"
        return user, None
    except Exception as e:
        logger.error(f"Error occurred while authenticating user: {e}", exc_info=True)
        return False, f"Error occurred: {e}"
