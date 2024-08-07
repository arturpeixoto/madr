from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Book, User
from madr.schemas import (
    BookList,
    BookPublic,
    BookSchema,
    BookUpdate,
    Message,
)
from madr.security import get_current_user

router = APIRouter(prefix='/books', tags=['books'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BookPublic)
def create_book(
    user: T_CurrentUser,
    book: BookSchema,
    session: T_Session,
):
    db_book = Book(
        title=book.title,
        year=book.year,
        user_id=user.id,
        author_id=book.author_id,
    )
    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.get('/', response_model=BookList)
def list_books(  # noqa
    session: T_Session,
    user: T_CurrentUser,
    title: str = Query(None),
    year: int = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    query = select(Book).where(Book.user_id == user.id)

    if title:
        query = query.filter(Book.title.contains(title))

    if year:
        query = query.filter(Book.year == year)

    books = session.scalars(query.offset(offset).limit(limit)).all()

    return {'books': books}


@router.patch(
    '/{book_id}', status_code=HTTPStatus.OK, response_model=BookPublic
)
def update_book(
    book_id: int, user: T_CurrentUser, session: T_Session, book: BookUpdate
):
    db_book = session.scalar(
        select(Book).where(Book.user_id == user.id, Book.id == book_id)
    )

    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.delete('/{book_id}', response_model=Message, status_code=HTTPStatus.OK)
def delete_book(book_id: int, session: T_Session, user: T_CurrentUser):
    db_book = session.scalar(
        select(Book).where(Book.user_id == user.id, Book.id == book_id)
    )

    if not db_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    session.delete(db_book)
    session.commit()

    return {'message': 'Book deleted'}
