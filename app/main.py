from fastapi import FastAPI, Depends
from pyodbc import Cursor

from app.database import get_db
from app.routers import listing
from app.routers import auth

app = FastAPI()
app.include_router(listing.router)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/{name}")
async def say_hi(name):
    return {"message": f"Hello {name}!"}


@app.get("/sqltest/")
async def sql_test(db: Cursor = Depends(get_db)):
    res = db.execute("SELECT @@VERSION;").fetchone()[0]
    return {"sql_version": res}
