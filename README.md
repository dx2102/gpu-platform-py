

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