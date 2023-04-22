import os

from fastapi import FastAPI, File, UploadFile, Response
from models import *
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

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
