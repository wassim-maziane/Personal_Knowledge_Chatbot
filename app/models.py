from pydantic import BaseModel
from fastapi import Cookie
from typing import Annotated


class QueryInput(BaseModel):
    question: str
    session_id: Annotated[str, Cookie()]


class QueryResponse(BaseModel):
    answer: str
    session_id: Annotated[str, Cookie()]
