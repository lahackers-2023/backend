import os

from fastapi import FastAPI, File, UploadFile, Response, status, Form
from fastapi.responses import JSONResponse
from typing_extensions import Annotated
from fastapi.middleware.cors import CORSMiddleware


import json
import psycopg2 
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

from models import *

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
async def upload_postcard(user_email: str, file: UploadFile = File(...)):
    """
    Returns the URL of the uploaded file in the format:
    {'url': [url]}
    """
    try:
        contents = file.file
        filename = file.filename
        s3_path = f"{user_email}/{filename}"

        s3_client = boto3.client(
            "s3",
            aws_access_key_id="AKIARO7I2FA42XVASXVN",
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        bucket_location = s3_client.get_bucket_location(Bucket="lahacks2023")
        try:
            s3_client.upload_fileobj(
                Fileobj=contents._file,
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