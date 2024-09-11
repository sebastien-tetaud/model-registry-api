# model-registry-api

## Local Installation on Linux
- Python 3.12 is required.
- Miniconda is recommended for managing Python environments.
### Download and Install Miniconda

```Bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
```

### Install dependencies

```Bash
pip install -r requirements.txt
```

### Export environment variable
In your linux terminal, export model regestry credential:

export mongo_username="your_username"
export mongo_password="your_password"
export mongo_host="model_regestry_host"
export mongo_auth_db="database_name"

Once edited, run the following cli:

```Bash
source ~/.bashrc
```

## Run the FastAPI

Run the following command:

```Bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
## Docker Deployement

TODO
