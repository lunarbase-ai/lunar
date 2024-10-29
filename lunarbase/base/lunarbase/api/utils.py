# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel

from core.lunarcore.utils import setup_logger

API_LOGGER = setup_logger("lunarbase-api")


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


class TimedLoggedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def timed_logged_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            API_LOGGER.info(
                f"{request.method} {request.url.path} returned {response.status_code} in {round(duration, 5)} seconds."
            )
            response.headers["X-Response-Time"] = str(duration)
            return response

        return timed_logged_route_handler
