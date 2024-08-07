from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from madr.database import get_session
from madr.models import Author, User
from madr.schemas import (
    AuthorList,
    AuthorPublic,
    AuthorSchema,
    AuthorUpdate,
    Message,
)
from madr.security import get_current_user

router = APIRouter(prefix='/authors', tags=['authors'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AuthorPublic)
def create_author(
    user: T_CurrentUser,
    author: AuthorSchema,
    session: T_Session,
):
    db_author = Author(name=author.name, created_by_user=user.id)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)

    return db_author


@router.get('/', response_model=AuthorList)
def list_authors(
    session: T_Session,
    user: T_CurrentUser,
    name: str = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    query = select(Author).where(Author.created_by_user == user.id)

    if name:
        query = query.filter(Author.name.contains(name))

    authors = session.scalars(query.offset(offset).limit(limit)).all()

    return {'authors': authors}


@router.patch(
    '/{author_id}', status_code=HTTPStatus.OK, response_model=AuthorPublic
)
def update_author(
    author_id: int,
    user: T_CurrentUser,
    session: T_Session,
    author: AuthorUpdate,
):
    db_author = session.scalar(
        select(Author).where(
            Author.created_by_user == user.id, Author.id == author_id
        )
    )

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    for key, value in author.model_dump(exclude_unset=True).items():
        setattr(db_author, key, value)

    session.add(db_author)
    session.commit()
    session.refresh(db_author)

    return db_author


@router.delete(
    '/{author_id}', response_model=Message, status_code=HTTPStatus.OK
)
def delete_author(author_id: int, session: T_Session, user: T_CurrentUser):
    db_author = session.scalar(
        select(Author).where(
            Author.created_by_user == user.id, Author.id == author_id
        )
    )

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    session.delete(db_author)
    session.commit()

    return {'message': 'Author deleted'}
