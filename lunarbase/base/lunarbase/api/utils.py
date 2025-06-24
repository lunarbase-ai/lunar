# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel

from lunarbase.utils import setup_logger

from lunarbase.api.component import ComponentAPI
from lunarbase.api.workflow import WorkflowAPI
from lunarbase.controllers.demo_controller import DemoController
from lunarbase.controllers.report_controller import ReportController
from lunarbase.controllers.file_controller import FileController
from lunarbase.controllers.code_completion_controller import CodeCompletionController
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.llm_controller import LLMController

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


class APIContextInitializer:
    @staticmethod
    def initialize_api_context(api_context):
        api_context.component_api = ComponentAPI(api_context.lunar_config)
        api_context.workflow_api = WorkflowAPI(api_context.lunar_config)
        api_context.demo_controller = DemoController(api_context.lunar_config)
        api_context.report_controller = ReportController(
            api_context.lunar_config,
            persistence_layer=api_context.lunar_registry.persistence_layer,
        )
        api_context.file_controller = FileController(
            api_context.lunar_config,
            persistence_layer=api_context.lunar_registry.persistence_layer,
        )
        api_context.code_completion_controller = CodeCompletionController(
            api_context.lunar_config
        )
        api_context.datasource_controller = DatasourceController(
            api_context.lunar_config,
        )
        api_context.llm_controller = LLMController(
            api_context.lunar_config,
        )
        api_context.component_api.index_global()


def initialize_api_context(api_context):
    APIContextInitializer.initialize_api_context(api_context)
    