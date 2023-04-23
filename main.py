from fastapi import FastAPI, File, UploadFile, Response, status, Form
from fastapi.responses import JSONResponse
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware


import json
import boto3
import psycopg2 
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
import shutil
from PIL import Image 
import io

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
async def upload_postcard(uid: str, file: UploadFile = File(...)):
    """
    Returns the URL of the uploaded file in the format:
    {'url': [url]}
    """
    def write_file(data, filename):
        # Convert binary data to proper format and write it on Hard Disk
        with open(filename, 'wb') as file:
            file.write(data)
    try:
        contents = file.file
        filename = file.filename
        write_file(file.file.read(), "image.jpg")
        pil_image = Image.open("image.jpg")
        in_mem_file = io.BytesIO()
        pil_image.save(in_mem_file, format=pil_image.format)
        in_mem_file.seek(0)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id="AKIARO7I2FA42XVASXVN",
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        print("BEORE s3 ")

        img_name = f"postcard{len(s3_client.list_objects_v2(Bucket='lahacks2023', Prefix=f'{uid}/'))}.jpg"
        s3_path = f"{uid}/{img_name}"
        bucket_location = s3_client.get_bucket_location(Bucket="lahacks2023")
        print(bucket_location)
        try:
            s3_client.upload_fileobj(
                Fileobj=in_mem_file,
                Bucket="lahacks2023",
                Key=s3_path,
                ExtraArgs={"ACL": "public-read"},
            )
        except Exception as e:
            print(e)

        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location["LocationConstraint"], "lahacks2023", s3_path
        )

        print(object_url)
        return {"url": object_url}
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
        if os.path.exists("image.jpg"):
            os.remove("image.jpg") 

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