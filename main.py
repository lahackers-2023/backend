from fastapi import FastAPI
from models import *

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/user/postcards")
async def get_postcards(user_email: str):
    return {"message": f"Getting postcards for {user_email}"}

@app.post("/postcards/add")
async def add_postcards():
    return {"message": "Hello World"}
