from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import static_content

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(static_content.router) 