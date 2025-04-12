from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete as sa_delete
from app import models, schemas, encryption
from app.cache import cache
import pytz

MIN_TTL_SECONDS = 300


async def create_secret(db: AsyncSession, data: schemas.SecretCreate, ip: str) -> str:
    ttl = max(data.ttl_seconds or MIN_TTL_SECONDS, MIN_TTL_SECONDS)
    expires_at = datetime.now(pytz.utc) + timedelta(seconds=ttl)

    encrypted_secret = encryption.encrypt_secret(data.secret)
    passphrase_hash = encryption.hash_passphrase(data.passphrase) if data.passphrase else None

    secret = models.Secret(
        secret_data=encrypted_secret,
        passphrase_hash=passphrase_hash,
        expires_at=expires_at
    )
    db.add(secret)
    await db.commit()
    cache.set(secret.id, encrypted_secret, ttl)
    log = models.SecretLog(secret_id=secret.id, action="create", ip_address=ip)
    db.add(log)
    await db.commit()

    return secret.id


async def get_secret(db: AsyncSession, secret_id: str, ip: str) -> str:
    cached = cache.get(secret_id)
    if cached:
        secret_data = encryption.decrypt_secret(cached)
        cache.delete(secret_id)
        await log_action(db, secret_id, "read", ip)
        await delete_secret_from_db(db, secret_id)
        return secret_data

    result = await db.execute(select(models.Secret).where(models.Secret.id == secret_id))
    secret = result.scalars().first()

    if not secret:
        raise ValueError("Secret not found or already retrieved")

    secret_expires_at_aware = secret.expires_at.astimezone(pytz.utc)
    current_time = datetime.now(pytz.utc)

    if secret_expires_at_aware and secret_expires_at_aware < current_time:
        await delete_secret_from_db(db, secret_id)
        raise ValueError("Secret expired")

    secret_data = encryption.decrypt_secret(secret.secret_data)
    await delete_secret_from_db(db, secret_id)
    cache.delete(secret_id)
    await log_action(db, secret_id, "read", ip)
    return secret_data


async def delete_secret(db: AsyncSession, secret_id: str, ip: str, passphrase: str = None):
    result = await db.execute(select(models.Secret).where(models.Secret.id == secret_id))
    secret = result.scalars().first()

    if not secret:
        raise ValueError("Secret not found")

    if secret.passphrase_hash and (
            not passphrase or not encryption.verify_passphrase(passphrase, secret.passphrase_hash)):
        raise ValueError("Invalid passphrase")

    await delete_secret_from_db(db, secret_id)
    cache.delete(secret_id)
    await log_action(db, secret_id, "delete", ip)


async def delete_secret_from_db(db: AsyncSession, secret_id: str):
    await db.execute(sa_delete(models.Secret).where(models.Secret.id == secret_id))
    await db.commit()


async def log_action(db: AsyncSession, secret_id: str, action: str, ip: str):
    log = models.SecretLog(secret_id=secret_id, action=action, ip_address=ip)
    db.add(log)
    await db.commit()
