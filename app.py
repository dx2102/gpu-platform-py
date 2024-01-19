




'''

pip install jupyter docker fastapi[all] python-jose passlib
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension github.copilot

curl ifconfig.io
uvicorn app:app --reload --host 0.0.0.0 --port 80

'''


import docker



from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from enum import Enum
from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException, status
app = FastAPI()
@app.get("/ping")
async def ping():
    return {"ping": "pong"}

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost", "https://localhost",
        # "https://dx2102.github.io",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.testclient import TestClient
client = TestClient(app)

from jose import JWTError, jwt

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from pydantic import BaseModel




# Auth: Signup and Login

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(weeks=1)

HTTP_401 = HTTPException(
    401,
    "Failed to authenticate",
)

class UserRole(str, Enum):
    admin = "admin"
    member = "member"
    guest = "guest"

class User(BaseModel):
    username: str
    hashed_password: str
    role: UserRole = UserRole.guest
    containers: list[str] = []

users_db = {
    "admin": User(
        username="admin",
        hashed_password="$2b$12$NAOsAVVlnjBnLbx3zqu6keb6gp7S7Kin1iA25.QdcrDSJlRFd68ey",
    ),
}

class Token(BaseModel):
    # Contains the jwt. Returned by /signup and /login
    token: str
    token_type: str

def sign_token(username: str) -> Token:
    return Token(
        token=jwt.encode(
            {
                "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE,
                "sub": username,
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        ),
        token_type="bearer",
    )

async def require_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTP_401
    username: str = payload.get("sub")
    if username is None:
        raise HTTP_401
    if username not in users_db:
        raise HTTP_401
    return users_db[username]

async def require_member(user = Depends(require_user)) -> User:
    if user.role == UserRole.guest:
        raise "You must be a member to access this resource."
    return user

async def require_admin(user = Depends(require_user)) -> User:
    if user.role != UserRole.admin:
        raise "You must be an admin to access this resource."
    return user

@app.get("/whoami")
async def whoami(user = Depends(require_user)):
    return user.username

class NewUser(BaseModel):
    username: str
    password: str

@app.post("/signup")
async def signup(form: NewUser):
    if form.username in users_db:
        raise HTTPException(400, detail="Username already taken")
    users_db[form.username] = User(
        username=form.username,
        hashed_password=pwd_context.hash(form.password),
    )
    return sign_token(form.username)

@app.post("/login")
async def login(form: NewUser) -> Token:
    if form.username not in users_db:
        raise HTTP_401
    user = users_db[form.username]
    if not pwd_context.verify(form.password, user.hashed_password):
        raise HTTP_401
    return sign_token(user.username)

@app.get("/users/me/", response_model=User)
async def users_me(user: User = Depends(require_user)):
    return user



# logged in team members can manage their containers
daemon = docker.from_env()

@app.get("/containers")
async def get_containers(user = Depends(require_member)):
    return [daemon.containers.Container.from_id(id).name for id in user.containers]










'''

curl ifconfig.io
uvicorn app:app --reload --host 0.0.0.0 --port 80

'''





















