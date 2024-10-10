# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import os.path
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, List, Dict

from dotenv import dotenv_values, set_key

from fastapi import (
    FastAPI,
    HTTPException,
    Body,
    UploadFile,
    File,
    responses,
    Query,
    status,
    APIRouter,
)

from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lunarcore.config import GLOBAL_CONFIG
from lunarcore.core.persistence import PersistenceLayer
from lunarcore.api.component import ComponentAPI
from lunarcore.api.utils import HealthCheck, TimedLoggedRoute, API_LOGGER
from lunarcore.api.workflow import WorkflowAPI
from lunarcore.core.controllers.code_completion_controller import (
    CodeCompletionController,
)
from lunarcore.core.controllers.file_controller import FileController
from lunarcore.core.controllers.report_controller import ReportController
from lunarcore.core.controllers.demo_controller import DemoController
from lunarcore.errors import ComponentError
from lunarcore.core.controllers.report_controller import ReportSchema
from lunarcore.core.data_models import (
    ComponentModel,
    WorkflowModel,
)
from lunarcore.core.auto_workflow import AutoWorkflow


# TODO: Async review

app = FastAPI(default_response_class=responses.ORJSONResponse)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["DELETE", "POST", "GET", "PUT", "OPTIONS"],
    allow_headers=["*"],
)
router = APIRouter(route_class=TimedLoggedRoute)
context = SimpleNamespace()


@app.on_event("startup")
async def app_startup():
    context.main_config = GLOBAL_CONFIG
    context.persistence_layer = PersistenceLayer(config=GLOBAL_CONFIG)
    context.persistence_layer.init_local_storage()

    # Normally the app will be started from CLI so maybe there is no need to register here
    # if len(COMPONENT_REGISTRY.components) == 0:
    #     await COMPONENT_REGISTRY.register(fetch=False)

    context.component_api = ComponentAPI(context.main_config)
    context.workflow_api = WorkflowAPI(context.main_config)
    context.demo_controller = DemoController(context.main_config)
    context.report_controller = ReportController(context.main_config)
    context.file_controller = FileController(context.main_config)
    context.code_completion_controller = CodeCompletionController(context.main_config)

    await context.component_api.index_global()


@app.get("/")
@app.post("/")
def read_root():
    raise HTTPException(
        status_code=404,
        detail="You seem to have lost your way. There is nothing here to see!",
    )


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Based on: https://gist.github.com/Jarmos-san/0b655a3f75b698833188922b714562e5
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


# @app.post("/login")
@router.post("/login")
def login(user_id: str):
    try:
        context.file_controller.persistence_layer.init_user_profile(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/list")
async def list_all_workflows(user_id: str):
    try:
        return await context.workflow_api.list_all(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/short_list")
async def list_all_short_workflows(user_id: str):
    try:
        return await context.workflow_api.list_short(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/search")
async def search_workflow(
    user_id: str,
    query: str = "",
):
    return await context.workflow_api.search(user_id, query)


@router.post("/workflow")
async def save_workflow(
    user_id: str = Query(..., description="User ID"),
    template_id: Optional[str] = Query(default=None, description="Template ID"),
    workflow: Optional[WorkflowModel] = None,
):
    if template_id is not None:
        workflow = context.demo_controller.get_by_id(template_id)
        new_id = str(uuid.uuid4())
        workflow.id = new_id
        for i, comp in enumerate(workflow.components):
            comp.workflow_id = new_id
            workflow.components[i] = comp
        await context.file_controller.copy_demo_files_to_workflow(
            demo_id=template_id, user_id=user_id, workflow_id=workflow.id
        )
    try:
        await context.workflow_api.save(user_id, workflow)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}")
async def get_workflow_by_id(workflow_id: str, user_id: str):
    try:
        return await context.workflow_api.get_by_id(workflow_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/workflow/{workflow_id}/notebook")
async def save_workflow_to_notebook(
    workflow_id: str, 
    user_id: str = Query(..., description="User ID")
):
    try:
        workflow = await context.workflow_api.get_by_id(workflow_id, user_id)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/workflow")
async def update_workflow(workflow: WorkflowModel, user_id: str):
    try:
        template = await context.workflow_api.update(workflow, user_id)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str, user_id: str):
    try:
        return await context.workflow_api.delete(workflow_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/run")
async def execute_workflow_by_id(workflow: WorkflowModel, user_id: str):
    try:
        return await context.workflow_api.run(workflow, user_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# @router.get("/workflow/status", response_model=WorkflowReturnModel)
# async def get_workflow_runtime(user_id: str, workflow_id: str):
#     pass


# @router.post("/workflow/pause", response_model=WorkflowRuntimeModel)
# async def pause_workflow_by_id(user_id: str, workflow_id: str):
#     pass


@router.post("/workflow/{workflow_id}/cancel")
async def cancel_workflow_by_id(user_id: str, workflow_id: str):
    try:
        await context.workflow_api.cancel(workflow_id=workflow_id, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content="")


@router.get("/component/list", response_model=List[ComponentModel])
async def list_components(user_id: str):
    try:
        return await context.component_api.list_all(user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component/search", response_model=List[ComponentModel])
async def search_component(query: str, user_id: str):
    try:
        return await context.component_api.search(query, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component/{component_id}", response_model=ComponentModel)
async def get_component_by_id(user_id: str, component_id: str):
    try:
        return await context.component_api.get_by_id(component_id, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/component", response_model=ComponentModel)
async def create_custom_component(
    user_id: str,
    custom_component: ComponentModel = Body(...),
):
    try:
        response = await context.component_api.create_custom_component(
            custom_component, user_id
        )
        return response
    except ComponentError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/component/run")
async def component_run(component: ComponentModel, user_id: str):
    try:
        return await context.component_api.run(component, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/component/{custom_component_id}")
async def delete_custom_component(custom_component_id: str, user_id: str):
    try:
        await context.component_api.delete_custom_component(
            custom_component_id, user_id
        )
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo/list")
def list_demos():
    try:
        return context.demo_controller.list_short()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report")
async def save_report(report: ReportSchema, user_id: str):
    try:
        return await context.report_controller.save(user_id, report)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report")
async def list_all_reports(user_id: str):
    try:
        return await context.report_controller.list_all(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report/{workflow_id}/{report_id}")
async def get_report_by_id(workflow_id: str, report_id: str, user_id: str):
    try:
        return await context.report_controller.get_by_id(
            user_id, workflow_id, report_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/file/{workflow_id}/upload")
async def upload_document(
    workflow_id: str,
    user_id: str,
    file: UploadFile = File(...),
):
    try:
        # file_name = file.filename
        return await context.file_controller.save(user_id, workflow_id, file)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="There was an error uploading the file: " + str(e),
        )


@router.get("/file/{workflow_id}")
async def get_files(
    user_id: str,
    workflow_id: str,
):
    return await context.file_controller.list_all_workflow_files(user_id, workflow_id)


@router.post("/code-completion")
def code_completion(
    code: str,
):
    try:
        return context.code_completion_controller.complete(code)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="There was an error completing the code: " + str(e),
        )


@router.get("/component/{component_label}/example")
async def get_component_example(user_id: str, component_label: str):
    eg_workflow = await context.component_api.get_example_workflow_by_label(
        component_label, user_id
    )

    if eg_workflow is not None:
        await context.workflow_api.save(user_id, eg_workflow)
    return eg_workflow


@router.post("/auto_workflow")
async def auto_create_workflow(
    auto_workflow: AutoWorkflow,
    user_id: str,
):
    try:
        await context.workflow_api.auto_create(auto_workflow, user_id)
        await context.component_api.save_auto_custom_components(
            auto_workflow.workflow.components, user_id
        )
        return auto_workflow.workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto_workflow_modification")
async def auto_modify_workflow(
    auto_workflow: AutoWorkflow, modification_instruction: str, user_id: str
):
    try:
        await context.workflow_api.auto_modify(
            auto_workflow, modification_instruction, user_id
        )
        await context.component_api.save_auto_custom_components(
            auto_workflow.workflow.components, user_id
        )
        return auto_workflow.workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environment")
def get_environment(user_id: str):
    try:
        env_path = context.persistence_layer.get_user_environment_path(user_id)
        if not os.path.isfile(env_path):
            environment = dict()
        else:
            environment = dict(dotenv_values(env_path))
        return JSONResponse(content=jsonable_encoder(environment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/environment")
def set_environment(user_id: str, environment: Dict = Body(...)):
    try:
        env_path = context.persistence_layer.get_user_environment_path(user_id)
        if os.path.isfile(env_path):
            Path(env_path).unlink(missing_ok=True)
        Path(env_path).touch(exist_ok=True)
        for variable, value in environment.items():
            if value is not None and len(str(value)) > 0:
                set_key(dotenv_path=env_path, key_to_set=variable, value_to_set=value)

        return JSONResponse(content=jsonable_encoder(environment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
