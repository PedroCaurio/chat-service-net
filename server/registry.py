'''
Responsável por desacoplar o loop principal da lógica de comandos através de um decorador.
Além disso, outras funções para facilitar o uso estão incluídas
'''
from functools import wraps
from typing import Any, Callable

_registry: list[tuple[str, Callable[..., None]]] = []

def register_command(name:str):
    def decorator(func: Callable[..., None]):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        
        _registry.append((name, wrapper))
        return wrapper
    
    return decorator

def get_registry() -> list[tuple[str, Callable[..., None]]]:
    return _registry.copy()

def get_command(name: str) -> Callable[..., Any] | None:
    for n, func in _registry:
        if n == name:
            return func
    return None