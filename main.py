from typing import Optional, Annotated
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, Query, Path, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uvicorn

from models import Contact, get_db, User
from pydantic_models import ContactModel, ContactModelResponse
from users import users_router, get_user
import logging

app = FastAPI(
    title="Контактна система",
    description="API для керування контактами та користувачами з використанням FastAPI",
    version="1.0.0"
)


app.include_router(users_router)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("")


@app.middleware("http")
async def test_middleware(request: Request, call_next) -> Response:
    x_custom_header = request.headers.get("X-Custom-Header")
    if not x_custom_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заголовок 'X-Custom Header' є обов'язковим")
    response: Response = await call_next(request)
    return response


@app.get("/message/")
async def test_message():
    print("Повідомлення від основної функції")
    return dict(msg="Тестове повідомлення")


@app.post(
    "/contacts/",
    tags=["Contacts"],
    summary="Додати новий контакт",
    description="Створює новий контакт у базі даних з усіма необхідними полями.",
    status_code=status.HTTP_201_CREATED,
    response_model=ContactModelResponse
)
async def add_contact(
    contact_model: ContactModel,
    db: Session = Depends(get_db),
    user: User = Depends(get_user)
):
    contact = Contact(**contact_model.model_dump(), id=uuid4().hex)
    db.add(contact)
    await db.commit()
    return contact

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
