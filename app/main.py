from fastapi import FastAPI, Depends, HTTPException, Request
from app import models, schemas, crud
from app.database import engine, get_db
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
import logging

app = FastAPI(title="Secret Service FastAPI")


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post("/secret", response_model=schemas.SecretResponse)
async def create_secret_endpoint(secret_in: schemas.SecretCreate, request: Request, db: AsyncSession = Depends(get_db)):
    ip = request.client.host
    try:
        secret_key = await crud.create_secret(db, secret_in, ip)
        return schemas.SecretResponse(secret_key=secret_key)
    except Exception as e:
        logging.error("Ошибка при создании секрета: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/secret/{secret_id}", response_model=schemas.SecretReadResponse)
async def get_secret_endpoint(secret_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    ip = request.client.host
    try:
        secret_text = await crud.get_secret(db, secret_id, ip)
        return schemas.SecretReadResponse(secret=secret_text)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/secret/{secret_id}", response_model=dict)
async def delete_secret_endpoint(secret_id: str, request: Request, data: schemas.SecretDeleteRequest,
                                 db: AsyncSession = Depends(get_db)):
    ip = request.client.host
    try:
        await crud.delete_secret(db, secret_id, ip, data.passphrase)
        return {"status": "secret_deleted"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
