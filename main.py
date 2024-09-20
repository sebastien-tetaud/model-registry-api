from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from pymongo import MongoClient
import os

from model_registry.user_manager import UserManager, PasswordGenerator
from model_registry.db_manager import DbManager
from loguru import logger
import secrets

app = FastAPI()

# MongoDB connection settings
MONGO_USERNAME = os.environ.get("mongo_username")
MONGO_PASSWORD = os.environ.get("mongo_password")
MONGO_HOST = os.environ.get("mongo_host")
MONGO_AUTH_DB = os.environ.get("mongo_auth_db")


# HTTP Basic Authentication object
security = HTTPBasic()

# Function to authenticate users using HTTP Basic Auth
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, MONGO_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, MONGO_PASSWORD)

    if not (correct_username and correct_password):
        logger.warning(f"Failed authentication attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    # If authentication is successful, establish MongoDB connection
    client = MongoClient(f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}/?authSource={MONGO_AUTH_DB}")
    return client

# Pydantic models for request data
class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str
    database: str


class DeleteUserRequest(BaseModel):
    username: str
    database: str


class StoreModelRequest(BaseModel):
    database: str
    collection: str
    modelPath: str
    modelArchitecture: str
    modelVersion: float
    project_name: str

    def to_metadata(self) -> dict:
        return {
            "model_architecture": self.modelArchitecture,
            "model_version": self.modelVersion,
            "project_name": self.project_name
        }


class DeleteModelRequest(BaseModel):
    database: str = "model_registry"
    collection: str = "llm"
    modelId: str = "66daf3cae7e64e7bde7f46a0"  # example ObjectId


class SearchModelRequest(BaseModel):
    database: str = "model_registry"
    collection: str = "llm"
    modelId: str = "66daf3cae7e64e7bde7f46a0"  # example ObjectId


class GetModelRequest(BaseModel):
    database: str = "model_registry"
    collection: str = "llm"
    modelId: str = "66daf3cae7e64e7bde7f46a0"  # example ObjectId

@app.post("/create_user")
def create_user(request: CreateUserRequest, client: MongoClient = Depends(authenticate)):
    """
    Create a new user in the specified MongoDB database.

    - **request** (CreateUserRequest): Contains the details for the user to be created.
    """
    try:
        user_manager = UserManager(client=client)
        user_manager.create_user(
            database=request.database,
            user=request.username,
            password=request.password,
            role=request.role
        )
        return {"message": f"User '{request.username}' created successfully in database '{request.database}'."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint to delete a user
@app.delete("/delete_user")
def delete_user(request: DeleteUserRequest, client: MongoClient = Depends(authenticate)):
    """
    Delete a user from the specified MongoDB database.

    - **request** (DeleteUserRequest): Contains the details for the user to be deleted.
    """
    try:
        user_manager = UserManager(client=client)
        user_manager.delete_user(
            database=request.database,
            user=request.username
        )
        return {"message": f"User '{request.username}' deleted successfully from database '{request.database}'."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/generate_password")
def generate_password(length: int = 12, special_chars: bool = False, credentials: HTTPBasicCredentials = Depends(authenticate)):
    """
    Generate a secure password.

    - **length** (int): Length of the password.
    - **special_chars** (bool): Whether to include special characters in the password.
    """
    password_generator = PasswordGenerator(length=length, include_special_chars=special_chars)
    return {"password": password_generator.generate()}


@app.post("/store_model")
async def store_model(request: StoreModelRequest, client: MongoClient = Depends(authenticate)):
    """
    Store a model in MongoDB GridFS with metadata.

    - **request** (StoreModelRequest): Contains database, collection, and metadata.
    - **file** (UploadFile): The model file to be stored.
    """
    try:
        dm = DbManager(client=client)
        # Generate metadata from the request
        metadata = request.to_metadata()
        # Call the store_model method to store the file in MongoDB GridFS
        result = dm.store_model(
            database=request.database,
            collection=request.collection,
            metadata=metadata,
            model_path=request.modelPath
        )

        if result:
            return {"message": "Model stored successfully."}
        else:
            return {"message": "Model already exists or could not be stored."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to delete a model by its ID
@app.delete("/delete_model")
def delete_model(request: DeleteModelRequest, client: MongoClient = Depends(authenticate)):
    """
    Delete a model from MongoDB GridFS using its ID.

    - **request** (DeleteModelRequest): Contains database, collection, and model_id.
    """
    try:
        dm = DbManager(client=client)
        dm.delete_model(
            database=request.database,
            collection=request.collection,
            model_id=request.modelId
        )
        return {"message": f"Model with ID '{request.modelId}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_model")
def search_model(request: SearchModelRequest, client: MongoClient = Depends(authenticate)):
    """
    Endpoint to search for a model by its model_id in MongoDB.
    """

    dm = DbManager(client=client)
    result = dm.search_model(database=request.database,
                             collection=request.collection,
                             model_id=request.modelId)
    if result:
        return {"status": "success", "model": result["metadata"]}
    else:
        raise HTTPException(status_code=404, detail="Model not found")


@app.post("/get_model")
async def get_model(request: GetModelRequest, client: MongoClient = Depends(authenticate)):
    """
    Endpoint to search for a model by its model_id in MongoDB.
    """

    dm = DbManager(client=client)
    result = dm.get_model(database=request.database,
                             collection=request.collection,
                             model_id=request.modelId)
    if result:
        return {"status": "success", "model": result["metadata"]}
    else:
        raise HTTPException(status_code=404, detail="Model not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
