from fastapi import FastAPI, File, UploadFile, Response, status, Form
from fastapi.responses import JSONResponse
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware


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

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def users_create_one(email: Annotated[str, Form()],
                           fname: Annotated[str, Form()],
                           lname: Annotated[str, Form()],
                           city: Annotated[str, Form()],
                           country: Annotated[str, Form()],
                           account_date: Annotated[str, Form()]
):
    
    if not (fname.isalpha()) or not (lname.isalpha()):
        return JSONResponse(
            status_code=500,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Invalid Name"
            }
        )
    print(email)
    print(fname)
    print(lname)
    print(country)
    print(city)
    print(account_date)
    try:
        print(f"INSERT INTO users ( email, fname, lname, city, country, account_date) VALUES ( {email}, {fname}, {lname}, {city}, {country}, {account_date})")
        cursor.execute(f"INSERT INTO users ( uid, email, fname, lname, city, country, account_date) VALUES ( DEFAULT, '{email}', '{fname}', '{lname}', '{city}', '{country}', (TIMESTAMP '{account_date}')) RETURNING *")
        connection.commit()
        print('update worked')
        res = cursor.fetchone()
        res['uid'] = str(res['uid'])
        res['account_date'] = str(res['account_date'])
        
        return JSONResponse(
                content= res,
                status_code=200
        )
    except (Exception, Error) as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal Server Error"
            }
        )

@app.get("/users")
async def users_get_all():
    try:
        cursor.execute("SELECT * from users ORDER BY users.uid")
        res = cursor.fetchall()
        for row in res:
            row['uid'] = str(row['uid'])
            row['account_date'] = str(row['account_date'])
        return JSONResponse(
                content=res,
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

@app.post("/getuser")
async def find_user(email: Annotated[str, Form()]):
    try:
        print(email)
        cursor.execute(f"SELECT users.uid from users WHERE users.email='{email}'")
        res = cursor.fetchone()
        if (res is None):
            return JSONResponse(
                content={},
                status_code=200
        )
        else:
            res['uid'] = str(res['uid'])
            return JSONResponse(
                content=res,
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