from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def read_root():
    return {
        'message': 'Olá mundo! Bem vindos ao Meu Acervo Digital de Romances'
    }
