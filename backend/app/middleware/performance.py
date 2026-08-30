import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# We use the standard Python logging here to capture the exact module name.
# If your custom logger from Module 2 uses a specific factory, you can import it instead.
logger = logging.getLogger(__name__)


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request/response details and measure API performance.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Start the timer
        start_time = time.perf_counter()

        # 2. Log the incoming request
        # We log the method and path. We avoid logging full URLs to prevent 
        # leaking sensitive query parameters in the logs.
        logger.info(f"--> {request.method} {request.url.path}")

        # 3. Process the request through the rest of the application
        try:
            response = await call_next(request)
        except Exception as e:
            # If an unhandled exception occurs, log it and re-raise 
            # so the Global Exception Handler (Module 3) can catch it.
            logger.error(f"!!! Exception in {request.url.path}: {str(e)}")
            raise e

        # 4. Calculate the process time
        process_time = time.perf_counter() - start_time
        process_time_ms = round(process_time * 1000, 2)

        # 5. Inject custom header for Frontend/Postman visibility
        response.headers["X-Process-Time"] = f"{process_time_ms} ms"
        
        # Optional: Inject a custom header to identify the API version/environment
        response.headers["X-API-Version"] = "1.0.0"

        # 6. Log the outgoing response
        logger.info(f"<-- {response.status_code} | {request.url.path} | {process_time_ms} ms")

        return response