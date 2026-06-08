try:
    from . import futures
except ImportError:
    import web.futures as futures


__all__ = ["futures"]
