"""Health check endpoint for liveness probe."""

from litestar import Router, get


@get("/live", sync_to_thread=False)
def liveness() -> dict[str, str]:
    """Liveness probe - confirms the process is running."""
    return {"status": "ok"}


health_router = Router(path="/health", route_handlers=[liveness])
