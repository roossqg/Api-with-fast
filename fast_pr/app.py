from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_pr.schemas import Mens

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Mens)
def root():
    return {'message': 'hello11'}


@app.get('/ht_res', response_class=HTMLResponse, status_code=200)
def hello1_htm():
    return """
    <html>
        <head>
            <title>page htm</title>
        </head>
        <body>
            <h2>Hello world!!</h2>
        </body>
    </html>
    """
