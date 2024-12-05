# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import dotenv_values, set_key
from fastapi import (
    APIRouter,
    Body,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
    responses,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from lunarbase import LUNAR_CONTEXT
from lunarbase.api.component import ComponentAPI
from lunarbase.api.typings import CodeCompletionRequestBody, ComponentPublishingRequestBody
from lunarbase.api.utils import HealthCheck, TimedLoggedRoute
from lunarbase.api.workflow import WorkflowAPI
from lunarbase.auto_workflow import AutoWorkflow
from lunarbase.controllers.code_completion_controller import CodeCompletionController
from lunarbase.controllers.component_controller.component_class_generator.component_class_generator import \
    get_component_code
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.demo_controller import DemoController
from lunarbase.controllers.file_controller import FileController
from lunarbase.controllers.llm_controller import LLMController
from lunarbase.controllers.report_controller import ReportController, ReportSchema
from lunarbase.components.errors import ComponentError
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel
from starlette.middleware.cors import CORSMiddleware

from copy import deepcopy

from lunarbase.modeling.datasources import DataSource
from lunarbase.modeling.llms import LLM

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
api_context = deepcopy(LUNAR_CONTEXT)


@app.on_event("startup")
async def app_startup():
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

    await api_context.component_api.index_global()


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
        api_context.lunar_registry.persistence_layer.init_user_profile(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/list")
async def list_all_workflows(user_id: str):
    try:
        return await api_context.workflow_api.list_all(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/short_list")
async def list_all_short_workflows(user_id: str):
    try:
        return await api_context.workflow_api.list_short(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/search")
async def search_workflow(
    user_id: str,
    query: str = "",
):
    return await api_context.workflow_api.search(user_id, query)


@router.post("/workflow")
async def save_workflow(
    user_id: str = Query(..., description="User ID"),
    template_id: Optional[str] = Query(default=None, description="Template ID"),
    workflow: Optional[WorkflowModel] = None,
):
    if template_id is not None:
        workflow = api_context.demo_controller.get_by_id(template_id)
        new_id = str(uuid.uuid4())
        workflow.id = new_id
        for i, comp in enumerate(workflow.components):
            comp.workflow_id = new_id
            workflow.components[i] = comp
        await api_context.file_controller.copy_demo_files_to_workflow(
            demo_id=template_id, user_id=user_id, workflow_id=workflow.id
        )
    try:
        await api_context.workflow_api.save(user_id, workflow)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}")
async def get_workflow_by_id(workflow_id: str, user_id: str):
    try:
        return await api_context.workflow_api.get_by_id(workflow_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workflow")
async def update_workflow(workflow: WorkflowModel, user_id: str):
    try:
        template = await api_context.workflow_api.update(workflow, user_id)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str, user_id: str):
    try:
        return await api_context.workflow_api.delete(workflow_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/run")
async def execute_workflow_by_id(workflow: WorkflowModel, user_id: str):
    try:
        return await api_context.workflow_api.run(workflow, user_id)
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
        await api_context.workflow_api.cancel(workflow_id=workflow_id, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content="")


@router.get("/component/list", response_model=List[ComponentModel])
async def list_components(user_id: str):
    try:
        return await api_context.component_api.list_all(user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component/search", response_model=List[ComponentModel])
async def search_component(query: str, user_id: str):
    try:
        return await api_context.component_api.search(query, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component/{component_id}", response_model=ComponentModel)
async def get_component_by_id(user_id: str, component_id: str):
    try:
        return await api_context.component_api.get_by_id(component_id, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/component", response_model=ComponentModel)
async def create_custom_component(
    user_id: str,
    custom_component: ComponentModel = Body(...),
):
    try:
        response = await api_context.component_api.create_custom_component(
            custom_component, user_id
        )
        return response
    except ComponentError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/component/run")
async def component_run(component: ComponentModel, user_id: str):
    try:
        return await api_context.component_api.run(component, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/component/{custom_component_id}")
async def delete_custom_component(custom_component_id: str, user_id: str):
    try:
        await api_context.component_api.delete_custom_component(
            custom_component_id, user_id
        )
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo/list")
def list_demos():
    try:
        return api_context.demo_controller.list_short()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report")
async def save_report(report: ReportSchema, user_id: str):
    try:
        return await api_context.report_controller.save(user_id, report)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report")
async def list_all_reports(user_id: str):
    try:
        return await api_context.report_controller.list_all(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report/{workflow_id}/{report_id}")
async def get_report_by_id(workflow_id: str, report_id: str, user_id: str):
    try:
        return await api_context.report_controller.get_by_id(
            user_id, workflow_id, report_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/file/{workflow_id}")
async def get_files(
    user_id: str,
    workflow_id: str,
):
    return await api_context.file_controller.list_all_workflow_files(
        user_id, workflow_id
    )


@router.post("/code-completion")
def code_completion(
    code: CodeCompletionRequestBody,
):
    try:
        return api_context.code_completion_controller.complete(code)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="There was an error completing the code: " + str(e),
        )


@router.get("/component/{component_label}/example")
async def get_component_example(user_id: str, component_label: str):
    eg_workflow = await api_context.component_api.get_example_workflow_by_label(
        component_label, user_id
    )

    if eg_workflow is not None:
        await api_context.workflow_api.save(user_id, eg_workflow)
    return eg_workflow


@router.post("/component/generate_class_code")
def generate_component_class(user_id: str, component:ComponentModel):
    return get_component_code(component)


@router.post("/component/publish")
async def publish_component(user_id: str, component_publishing_input: ComponentPublishingRequestBody):
    await api_context.component_api.publish_component(
        component_publishing_input.author,
        component_publishing_input.author_email,
        component_publishing_input.component_name,
        component_publishing_input.component_description,
        component_publishing_input.component_class,
        component_publishing_input.component_documentation,
        component_publishing_input.version,
        component_publishing_input.access_token,
        user_id
    )


@router.post("/auto_workflow")
async def auto_create_workflow(
    auto_workflow: AutoWorkflow,
    user_id: str,
):
    try:
        await api_context.workflow_api.auto_create(auto_workflow, user_id)
        await api_context.component_api.save_auto_custom_components(
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
        await api_context.workflow_api.auto_modify(
            auto_workflow, modification_instruction, user_id
        )
        await api_context.component_api.save_auto_custom_components(
            auto_workflow.workflow.components, user_id
        )
        return auto_workflow.workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environment")
def get_environment(user_id: str):
    try:
        env_path = (
            api_context.lunar_registry.persistence_layer.get_user_environment_path(
                user_id
            )
        )
        if not Path(env_path).is_file():
            environment = dict()
        else:
            environment = dict(dotenv_values(env_path))
        return JSONResponse(content=jsonable_encoder(environment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/environment")
def set_environment(user_id: str, environment: Dict = Body(...)):
    try:
        env_path = (
            api_context.lunar_registry.persistence_layer.get_user_environment_path(
                user_id
            )
        )
        if Path(env_path).is_file():
            Path(env_path).unlink(missing_ok=True)
        Path(env_path).touch(exist_ok=True)
        for variable, value in environment.items():
            if value is not None and len(str(value)) > 0:
                set_key(dotenv_path=env_path, key_to_set=variable, value_to_set=value)

        return JSONResponse(content=jsonable_encoder(environment))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasource", response_model=List[DataSource])
async def get_datasource(user_id: str, filters: Optional[Dict] = None):
    try:
        return await api_context.datasource_controller.get_datasource(user_id, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasource", response_model=DataSource)
async def create_datasource(user_id: str, datasource: Dict = Body(...)):
    try:
        return await api_context.datasource_controller.create_datasource(
            user_id, datasource
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/datasource", response_model=DataSource)
async def update_datasource(user_id: str, datasource: Dict = Body(...)):
    try:
        return await api_context.datasource_controller.update_datasource(
            user_id, datasource
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/datasource/{datasource_id}")
async def delete_datasource(user_id: str, datasource_id: str):
    try:
        return await api_context.datasource_controller.delete_datasource(
            user_id, datasource_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasource/{datasource_id}/upload")
async def upload_file(
    user_id: str,
    datasource_id: str,
    file: UploadFile = File(...),
):
    try:
        return await api_context.datasource_controller.upload_local_file(
            user_id, datasource_id, file
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="There was an error uploading the file: " + str(e),
        )

@router.get("/datasource/types")
def get_datasource_types():
    try:
        return DatasourceController.get_datasource_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)
)

@router.get("/llm", response_model=List[LLM])
async def get_llm(user_id: str, filters: Optional[Dict] = None):
    try:
        return await api_context.llm_controller.get_llm(user_id, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm", response_model=LLM)
async def create_llm(user_id: str, llm: Dict = Body(...)):
    try:
        return await api_context.llm_controller.create_llm(user_id, llm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/llm", response_model=LLM)
async def update_llm(user_id: str, llm: Dict = Body(...)):
    try:
        return await api_context.llm_controller.update_llm(user_id, llm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/llm/{llm_id}")
async def delete_llm(user_id: str, llm_id: str):
    try:
        return await api_context.llm_controller.delete_llm(user_id, llm_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/llm/types")
def get_llm_types():
    try:
        return LLMController.get_llm_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
