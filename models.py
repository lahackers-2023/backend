from pydantic import BaseModel
from typing import Union
import datetime



class Postcard(BaseModel):
    sender_email: str
    receiver_email: str
    image_url: str
    message: str
    sent_timestamp: datetime.datetime
