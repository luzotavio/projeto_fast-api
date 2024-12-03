from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.get('/html', response_class=HTMLResponse)
def read_htmlt():
    return """
        <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Exemplo Olá Mundo</title>
    </head>
    <body>
        <h1>Olá, Mundo!</h1>
    </body>
    </html>
    """
