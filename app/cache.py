import time
from typing import Any, Optional
from threading import Lock


class InMemoryCache:
    def __init__(self):
        self._store = {}
        self._lock = Lock()

    def set(self, key: str, value: Any, ttl: int):
        expire_at = time.time() + ttl
        with self._lock:
            self._store[key] = (value, expire_at)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, expire_at = item
            if expire_at < time.time():
                del self._store[key]
                return None
            return value

    def delete(self, key: str):
        with self._lock:
            self._store.pop(key, None)

    def cleanup(self):
        with self._lock:
            now = time.time()
            expired_keys = [key for key, (_, exp) in self._store.items() if exp < now]
            for key in expired_keys:
                del self._store[key]


cache = InMemoryCache()
