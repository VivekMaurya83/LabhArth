"""
LabhArth AI — API Middleware
===============================
Middlewares for CORS, Request Logging, Exception Handling, Request ID, and Latency tracking.
"""

import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.utils.logger import logger


class RequestLifecycleMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages the lifecycle of an HTTP request:
    - Generates and injects a unique X-Request-ID.
    - Measures request execution latency.
    - Logs details of incoming requests and outgoing responses.
    - Catches all unhandled exceptions globally and formats a consistent error response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Request ID Generation/Propagation
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # 2. Timing starting point
        start_time = time.perf_counter()

        # 3. Log incoming request
        logger.info(
            f"--> [{request_id}] {request.method} {request.url.path} | "
            f"Headers: {dict(request.headers)} | "
            f"Params: {dict(request.query_params)}"
        )

        try:
            # 4. Process the request
            response = await call_next(request)

            # 5. Measure latency
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            # 6. Inject custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

            # 7. Log outgoing response status and duration
            logger.info(
                f"<-- [{request_id}] Status: {response.status_code} | "
                f"Duration: {duration_ms:.2f}ms"
            )
            return response

        except Exception as exc:
            # 8. Global Unhandled Exception Handling
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"[ERROR] Unhandled Exception [{request_id}] during {request.method} {request.url.path} "
                f"after {duration_ms:.2f}ms: {exc}",
                exc_info=True
            )

            # Return a consistent JSON error response
            from backend.utils.config import get_settings
            settings = get_settings()

            err_detail = "Internal Server Error"
            err_msg = str(exc)
            
            # Hide detailed error messages in production env
            if settings.is_production:
                err_detail = "An internal server error occurred. Please try again later."
                err_msg = "Hidden"

            return JSONResponse(
                status_code=500,
                content={
                    "detail": err_detail,
                    "error": err_msg,
                    "request_id": request_id,
                    "status_code": 500
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Process-Time-Ms": f"{duration_ms:.2f}"
                }
            )
