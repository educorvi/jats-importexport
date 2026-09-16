"""Process bootstrap for the API and its Prometheus metrics server."""

import os
import tempfile
from pathlib import Path

from api.config import APIConfig


def _configure_prometheus_multiprocess_dir() -> tuple[Path, bool]:
    """Configure multiprocess mode before prometheus_client is imported."""
    configured_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
    if configured_dir:
        metrics_dir = Path(configured_dir)
        metrics_dir.mkdir(parents=True, exist_ok=True)
        return metrics_dir, False

    metrics_dir = Path(tempfile.mkdtemp(prefix="jats-importexport-prometheus-"))
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(metrics_dir)
    return metrics_dir, True


def start() -> None:
    """Console script entry point – run with ``uv run start-api``."""
    metrics_dir, remove_metrics_dir = _configure_prometheus_multiprocess_dir()

    # These imports must happen after PROMETHEUS_MULTIPROC_DIR is configured.
    import uvicorn
    from prometheus_client import (
        CollectorRegistry,
        GCCollector,
        PlatformCollector,
        ProcessCollector,
        multiprocess,
    )
    from prometheus_client.exposition import start_http_server

    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    GCCollector(registry=registry)
    PlatformCollector(registry=registry)
    ProcessCollector(registry=registry)

    server, thread = start_http_server(APIConfig.METRICS_PORT, registry=registry)
    try:
        uvicorn.run(
            "api.main:app",
            host=APIConfig.HOST,
            port=APIConfig.PORT,
            reload=APIConfig.RELOAD,
            workers=APIConfig.WORKERS,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
        if remove_metrics_dir:
            for metrics_file in metrics_dir.glob("*.db"):
                metrics_file.unlink()
            metrics_dir.rmdir()
