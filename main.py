from fastapi import FastAPI, File, UploadFile, Response, status, Body
from fastapi.responses import JSONResponse
# from pydantic import BaseModel

import json
import psycopg2 
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

from models import *

import os
from dotenv import load_dotenv
load_dotenv()

class User(BaseModel):
    fname: str
    lname: str
    city: str
    country: str
    account_date: str

db_url = f"postgresql://{os.getenv('CDB_USER')}:{os.getenv('CDB_PASSWORD')}@{os.getenv('CDB_HOST')}:{os.getenv('CDB_PORT')}/{os.getenv('CDB_DB_NAME')}?sslmode=prefer"

connection = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
cursor = connection.cursor()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/user/postcards")
async def get_postcards(user_email: str):
    return {"message": f"Getting postcards for {user_email}"}

@app.post("/postcard/crop")
async def crop_postcard(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        return Response(content=contents, media_type="image/png")
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

@app.post("/postcard/upload")
async def upload_postcard(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        return Response(content=contents, media_type="image/png")
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

@app.post("/postcard/add")
async def add_postcards():
    return {"message": "Hello World"}

@app.post("/users")
async def users_create_one(user: User):
    return user
    # if not (data.fname.isalpha()) or not (data.lname.isalpha()):
    #     return JSONResponse(
    #         status_code=500,
    #         content={
    #             "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             "message": "Invalid Name"
    #         }
    #     )

    # try:
    #     cursor.execute(f"INSERT INTO users (uid, email, fname, lname, city, country, account_date) VALUES (DEFAULT, {data.email}, {data.fname}, {data.lname}, {data.city}, {data.country}, {data.account_date})")
    #     connection.commit()
    #     res = cursor.fetchone()
    #     res['uid'] = str(res['uid'])
        
    #     return JSONResponse(
    #             json.dumps(res),
    #             status_code=200
    #     )
    # except:
    #     return JSONResponse(
    #         status_code=500,
    #         content={
    #             "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             "message": "Internal Server Error"
    #         }
    #     )

@app.get("/users")
async def users_get_all():
    try:
        cursor.execute("SELECT * from users ORDER BY users.uid")
        res = cursor.fetchall()
        for row in res:
            row['id'] = str(row['id'])
        return JSONResponse(
                json.dumps(res),
                status_code=200
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": f"Internal Server Error {e}"
            }
        )

