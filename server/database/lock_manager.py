import threading
from contextlib import contextmanager
from typing import Iterable


collection_locks: dict[str, threading.RLock] = {}
collection_locks_lock = threading.Lock()


def get_or_create(name: str) -> threading.RLock:
    """Retorna um RLock para a coleção `name`, criando se necessário (thread-safe)."""
    with collection_locks_lock:
        lk = collection_locks.get(name)
        if lk is None:
            lk = threading.RLock()
            collection_locks[name] = lk
        return lk


@contextmanager
def lock_collections(names: Iterable[str]):
    """Adquire locks para as coleções e libera ao final."""
    ordered = sorted({str(n) for n in names})
    acquired: list[threading.RLock] = []
    try:
        for name in ordered:
            lk = get_or_create(name)
            lk.acquire()
            acquired.append(lk)
        yield
    finally:
        # libera na ordem inversa
        for lk in reversed(acquired):
            try:
                lk.release()
            except RuntimeError:
                # se já liberado ou incapaz, ignorar
                pass


def get_lock(name: str) -> threading.RLock:
    """Acesso direto ao lock."""
    return get_or_create(name)
