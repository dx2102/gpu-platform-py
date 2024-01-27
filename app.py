




'''

pip install jupyter docker fastapi[all] python-jose passlib
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
code --install-extension github.copilot

curl ifconfig.io
uvicorn app:app --host 0.0.0.0 --port 80 --reload 
nohup uvicorn app:app --host 0.0.0.0 --port 80 --reload &

'''

import psutil
import docker
import random


from datetime import datetime, timedelta, timezone
from typing import Annotated, Union
from enum import Enum
from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException, status
app = FastAPI()
@app.get("/ping")
async def ping():
    return {"ping": "pong"}

# mount the website, redirects
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
@app.get("/")
async def root():
    return RedirectResponse(url="/gpu-platform-vue/index.html")
app.mount("/gpu-platform-vue", StaticFiles(directory="dist"), name="gpu-platform-vue")

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from starlette.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        # "https://dx2102.github.io",
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








# NOTE: authentication part

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
    containers: list[docker.models.containers.Container] = []
    class Config:
        arbitrary_types_allowed=True

    def reload_containers(self):
        # clear dead containers
        new_lst = []
        for container in self.containers:
            try:
                container.reload()
            except docker.errors.NotFound:
                container.remove(force=True)
                continue
            if container.status == "exited":
                container.remove(force=True)
                continue
            new_lst.append(container)
        self.containers = new_lst
        return self.containers
    


users_db = {
    "admin": User(
        username="admin",
        hashed_password="$2b$12$NAOsAVVlnjBnLbx3zqu6keb6gp7S7Kin1iA25.QdcrDSJlRFd68ey",
        role=UserRole.admin,
    ),
    "guest": User(
        username="guest",
        hashed_password="$2b$12$NAOsAVVlnjBnLbx3zqu6keb6gp7S7Kin1iA25.QdcrDSJlRFd68ey",
        role=UserRole.guest,
    ),
}
# duckdb

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
        raise HTTPException(403, "You must be a member to access this resource.")
    return user

async def require_admin(user = Depends(require_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(403, "You must be an admin to access this resource.")
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


















# NOTE: container logic part
 
# import requests
# public_ip = requests.get('https://ipconfig.io/ip').text.strip()
# print(f"Local IP: {public_ip}")
public_ip = "150.109.4.158"
print()
print(f"Server is at: http://{public_ip}/gpu-platform-vue")
print()

daemon = docker.from_env()

max_containers = 2
current_containers = 0

resource_per_gpu = {
    "cpus": 1,
    "memory": "2G",
    "gpus": 0,
    "disk": "40G",
}

host_info = {
    "cpu_name": "*",
    "gpu_name": "*",
    "video_memory": 0,
    "cuda_version": "*",
}

cpu_count = psutil.cpu_count()
if resource_per_gpu["cpus"] * max_containers > cpu_count:
    raise Exception("Not enough cpus for the requested number of containers")
cpu_pool = list(range(cpu_count))





@app.get("/resources")
async def resources(user = Depends(require_member)):
    return {
        "max_containers": max_containers,
        "current_containers": current_containers,
        **resource_per_gpu,
        **host_info,
    }

def new_container():
    password = str(random.randint(100000, 999999))
    cpus = random.sample(cpu_pool, resource_per_gpu["cpus"])
    for cpu in cpus:
        cpu_pool.remove(cpu)

    container = daemon.containers.run(
        "my-python-env",
        detach=True,
        ports={
            # exposes container's ssh, jupyter, and http ports to the host
            # 0 means we let docker choose a random available port on the host
            22: 0,
            8888: 0,
            80: 0,
        },
        # cpu, memory, and disk limits
        cpuset_cpus=",".join([str(cpu) for cpu in cpus]),
        mem_limit=resource_per_gpu["memory"],
        # this only works in XFS filesystems, not ext4
        # storage_opt={"size": resource_per_gpu["disk"]},
        device_requests=[
            # gpus will be set here if available
            # docker.types.DeviceRequest(device_ids=["0,1"], capabilities=[['gpu']])
        ],

        labels=["my-python-env"],
        environment={
            "PASSWORD": password,
        },
    )
    return container

def log_container_json(container):
    # summarize container info above into a json
    global daemon, public_ip
    short_id = container.short_id
    container.reload()
    status = container.status
    ports = container.attrs["NetworkSettings"]["Ports"]
    ssh_port = ports["22/tcp"][0]["HostPort"]
    jupyter_port = ports["8888/tcp"][0]["HostPort"]

    ssh_command = f"ssh -p {ssh_port} root@{public_ip}"
    password = container.attrs["Config"]["Env"][0].split("=")[1]

    logs = container.logs().decode("utf-8")
    line = [line for line in logs.split("\n") if "?token=" in line]
    if len(line) == 0:
        jupyter_token = ""
        jupyter_command = ""
    else:
        token = line[0].split("?token=")[1]
        jupyter_token = token
        jupyter_command = f"http://{public_ip}:{jupyter_port}/lab?token={token}"
    
    # cpus = container.attrs["HostConfig"]["CpusetCpus"]
    # memory = container.attrs["HostConfig"]["MemorySwap"]
    # gpus = container.attrs["HostConfig"]["DeviceRequests"]

    cpus = resource_per_gpu["cpus"]
    memory = resource_per_gpu["memory"]
    gpus = resource_per_gpu["gpus"]

    keys = [
        "short_id",
        "status",
        "cpus",
        "memory",
        "gpus",
        "ssh_command",
        "password",
        "jupyter_command",
    ]
    vars = locals()
    return {key: vars[key] for key in keys} 



@app.post("/containers")
async def create_container(user = Depends(require_member)):
    global current_containers
    if current_containers >= max_containers:
        raise HTTPException(400, detail="Too many containers")
    container = new_container()
    current_containers += 1
    user.containers.append(container)
    return {"id": container.short_id}

@app.get("/containers")
async def list_containers(user = Depends(require_member)):
    user.reload_containers()
    return [log_container_json(container) for container in user.containers]

@app.delete("/containers/{id}")
async def delete_container(id: str, user = Depends(require_member)):
    for container in user.containers:
        if container.short_id == id:
            container.remove(force=True)
            # docker rm -f $id
            user.containers.remove(container)
            global current_containers
            current_containers -= 1
            cpu_pool.extend([int(cpu) for cpu in container.attrs["HostConfig"]["CpusetCpus"].split(",")])
            return {"id": id}
    raise HTTPException(404, detail="Container not found")



    









'''

curl ifconfig.io
uvicorn app:app --reload --host 0.0.0.0 --port 80

'''











'''

加上镜像、文件存储、计时和历史
用户信息存进数据库
前后端写一些文档
API也要写文档

'''









