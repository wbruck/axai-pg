from functools import wraps
import time
from typing import Callable, Any, Type, TypeVar
from .repository_interface import MODEL_MAPPINGS
import asyncio

T = TypeVar('T')

def track_metrics(model_class: Type[T], slow_query_threshold_ms: float = 1000.0):
    """
    Decorator to track repository operation metrics.
    
    Args:
        model_class: The model class being operated on
        slow_query_threshold_ms: Threshold in milliseconds to mark a query as slow
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get repository instance from first argument (self)
            if not args:
                return await func(*args, **kwargs)
                
            repository = args[0]
            if not hasattr(repository, '_metrics'):
                return await func(*args, **kwargs)
            
            start_time = time.time()
            error_occurred = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                is_slow = duration_ms > slow_query_threshold_ms
                
                repository._metrics.record_operation(
                    duration_ms=duration_ms,
                    error=error_occurred,
                    slow=is_slow
                )
                
                if is_slow:
                    # Log slow query for monitoring
                    print(f"WARNING: Slow query detected in {repository.__class__.__name__}.{func.__name__}: {duration_ms:.2f}ms")
        
        return wrapper
    return decorator

def with_metrics(cls):
    """Class decorator to automatically add metrics tracking to all async methods."""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith('_'):
            if asyncio.iscoroutinefunction(attr_value):
                setattr(cls, attr_name, track_metrics(cls.model_class)(attr_value))
    return cls
