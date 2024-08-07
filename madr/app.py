from http import HTTPStatus

from fastapi import FastAPI

from madr.routers import auth, authors, books, users
from madr.schemas import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(authors.router)
app.include_router(users.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {
        'message': 'Olá mundo! Bem vindos ao Meu Acervo Digital de Romances'
    }
