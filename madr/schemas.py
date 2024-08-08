from datetime import datetime

from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class BookSchema(BaseModel):
    title: str
    year: int
    author_id: int | None


class BookPublic(BookSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class BookList(BaseModel):
    books: list[BookPublic]


class BookUpdate(BaseModel):
    title: str | None = None
    year: int | None = None
    author_id: int | None = None


class AuthorSchema(BaseModel):
    name: str


class AuthorPublic(AuthorSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class AuthorList(BaseModel):
    authors: list[AuthorPublic]


class AuthorUpdate(BaseModel):
    name: str | None = None
