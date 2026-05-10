import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_pr.routers import auth, to_do, users
from fast_pr.schemas import Mens

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# applications plugin:
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(to_do.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Mens)
async def root():
    return {'message': 'hello'}


@app.get('/ht_res', response_class=HTMLResponse, status_code=200)
async def hello1_htm():
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


# index is not database id
