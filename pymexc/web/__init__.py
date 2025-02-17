try:
    from . import futures
except ImportError:
    import futures


__all__ = ["futures"]
