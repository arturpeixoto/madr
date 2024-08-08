import re
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


def sanitize_string(value: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', value)).strip().lower()


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AuthorPublic)
def create_author(
    user: T_CurrentUser,
    author: AuthorSchema,
    session: T_Session,
):
    sanitized_name = sanitize_string(author.name)
    existing_author = session.scalar(
        select(Author).where(Author.name == sanitized_name)
    )
    if existing_author:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Author with the same name already exists',
        )

    db_author = Author(name=sanitized_name, created_by_user=user.id)
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
    query = session.query(Author)
    if name:
        sanitized_name = sanitize_string(name)
        query = query.filter(Author.name.contains(sanitized_name))

    authors = session.scalars(query.offset(offset).limit(limit)).all()

    return {'authors': authors}


@router.get(
    '/{author_id}', response_model=AuthorPublic, status_code=HTTPStatus.OK
)
def get_author_by_id(author_id: int, session: T_Session, user: T_CurrentUser):
    db_author = session.scalar(
        select(Author).where(
            Author.id == author_id,
        )
    )

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    return db_author


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
            Author.id == author_id,
        )
    )

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )
    
    if db_author.created_by_user != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to modify this author',
        )

    if 'name' in author.model_dump(exclude_unset=True):
        sanitized_name = sanitize_string(author.name)
        existing_author = session.scalar(
            select(Author).where(
                Author.name == sanitized_name,
            )
        )
        if existing_author and existing_author.id != author_id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Author with the same name already exists',
            )
        setattr(db_author, 'name', sanitized_name)

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
            Author.id == author_id,
        )
    )

    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )
    
    if db_author.created_by_user != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to delete this author',
        )

    session.delete(db_author)
    session.commit()

    return {'message': 'Author deleted'}
