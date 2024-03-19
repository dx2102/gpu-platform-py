
## What is this?
This is a simple web project to help manage GPU machines using Docker. It is like a simple web version of Docker Desktop. 

## What is Docker?

Docker is like a weaker and more lightweight version of a virtual machine. 

You can start multiple Docker containers on the same machine. Each container will behave like an isolated operating system. 

Docker is more lightweight than virutal machine in that all containers share the same kernel of the host operating system. A lot of mechanisms are achieved using renaming rather than simulating. Therefore Docker starts faster and uses less resources than virtual machines.

Besides merely creating containers, you can manage images, volumes, and networks of containers. Docker Hub is a cloud repository to store images. You can also orchestrate containers on different machines using Docker Compose or Kubernetes to achieve things like auto-scaling, auto-recovery, load balancing, etc.


## Project components

Frontend code is in the `gpu-platform-vue` repo. The frontend uses Vue, Naive UI, and Tailwind CSS. The backend uses FastAPI and Docker Python SDK.

This is a very simple project, but it demonstrates basic configuration for FastAPI and Vue, as well as JWT authentication.

All backend code is currently only in `app.py`. Vue code is built and moved into `dist`. Other files in this repo are test files trying to interact with Docker SDK.

Docker provides a SDK (library) in Python to interact with the Docker Daemon. You may want to look at the code trying to extract information from returned objects.

## Install and run

To run this project, you need to have a machine with public IP and Python and Docker installed.

Clone the repo:
```
cd [where you want to save the repo]
git clone https://github.com/dx2102/gpu-platform-py
cd gpu-platform-py
```

Install these dependencies:
```
pip install jupyter docker fastapi[all] python-jose passlib
```


Build the basic image on your machine:
```
cd container
docker build -t my-python-env .
```

Run app.py
```
uvicorn app:app --reload
```

## Backend APIs 

### (work in progress)

/ping: get

/signup: post

/login: post

/users/me: get

---

/resources: get

/containers: post, get

/containers/{id}: delete