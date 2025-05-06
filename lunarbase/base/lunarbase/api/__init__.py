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
from fastapi.responses import StreamingResponse

from lunarbase.api.typings import CodeCompletionRequestBody, ComponentPublishingRequestBody
from lunarbase.api.utils import HealthCheck, TimedLoggedRoute
from lunarbase.controllers.component_controller.component_class_generator.component_class_generator import \
    get_component_code
from lunarbase.controllers.datasource_controller import DatasourceController

from lunarbase.controllers.llm_controller import LLMController
from lunarbase.controllers.report_controller import ReportSchema
from lunarbase.components.errors import ComponentError
from lunarbase.modeling.data_models import ComponentModel, WorkflowModel
from starlette.middleware.cors import CORSMiddleware
from lunarbase import lunar_context_factory


from lunarbase.modeling.datasources import DataSource
from lunarbase.modeling.llms import LLM
from lunarbase.utils import setup_logger

# TODO: review

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

api_context = lunar_context_factory()
api_context.lunar_registry.load_cached_components()
api_context.lunar_registry.register()

logger = setup_logger("api")

@app.on_event("startup")
async def app_startup():
    api_context.component_api.index_global()


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
def list_all_workflows(user_id: str):
    try:
        return api_context.workflow_api.list_all(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/short_list")
def list_all_short_workflows(user_id: str):
    try:
        return api_context.workflow_api.list_short(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/search")
def search_workflow(
    user_id: str,
    query: str = "",
):
    return api_context.workflow_api.search(user_id, query)


@router.post("/workflow")
def save_workflow(
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
        api_context.file_controller.copy_demo_files_to_workflow(
            demo_id=template_id, user_id=user_id, workflow_id=workflow.id
        )
    try:
        api_context.workflow_api.save(user_id, workflow)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}")
def get_workflow_by_id(workflow_id: str, user_id: str):
    try:
        return api_context.workflow_api.get_by_id(workflow_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/workflow")
def update_workflow(workflow: WorkflowModel, user_id: str):
    try:
        template = api_context.workflow_api.update(workflow, user_id)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/workflow/{workflow_id}")
def delete_workflow(workflow_id: str, user_id: str):
    try:
        return api_context.workflow_api.delete(workflow_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/run")
async def execute_workflow_by_id(workflow: WorkflowModel, user_id: str):
    try:
        return await api_context.workflow_api.run(workflow, user_id)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/workflow/stream")
async def stream_workflow(workflow_id: str, user_id: str):
    return StreamingResponse(
        api_context.workflow_api.stream_workflow_by_id(workflow_id, user_id),
        media_type="text/event-stream"
    )


# @router.get("/workflow/status", response_model=WorkflowReturnModel)
# def get_workflow_runtime(user_id: str, workflow_id: str):
#     pass


# @router.post("/workflow/pause", response_model=WorkflowRuntimeModel)
# def pause_workflow_by_id(user_id: str, workflow_id: str):
#     pass


@router.post("/workflow/{workflow_id}/cancel")
def cancel_workflow_by_id(user_id: str, workflow_id: str):
    try:
        api_context.workflow_api.cancel(workflow_id=workflow_id, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content="")


@router.get("/workflow/{workflow_id}/inputs")
async def get_workflow_inputs(user_id: str, workflow_id: str):
    return await api_context.workflow_api.get_workflow_component_inputs(workflow_id, user_id)


@router.get("/workflow/{workflow_id}/outputs")
async def get_workflow_outputs(user_id: str, workflow_id: str):
    return await api_context.workflow_api.get_workflow_component_outputs(workflow_id, user_id)


@router.post("/workflow/{workflow_id}/run")
async def run_workflow_by_id(user_id: str, workflow_id: str, body: Dict = Body(...)):
    return await api_context.workflow_api.run_workflow_by_id(workflow_id, body["inputs"], user_id)


@router.get("/component/list", response_model=List[ComponentModel])
def list_components(user_id: str):
    try:
        return api_context.component_api.list_all(user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component/search", response_model=List[ComponentModel])
def search_component(query: str, user_id: str):
    try:
        return api_context.component_api.search(query, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/component/{component_id}", response_model=ComponentModel)
def get_component_by_id(user_id: str, component_id: str):
    try:
        return api_context.component_api.get_by_id(component_id, user_id)
    except ComponentError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/component", response_model=ComponentModel)
def create_custom_component(
    user_id: str,
    custom_component: ComponentModel = Body(...),
):
    try:
        response = api_context.component_api.create_custom_component(
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
def delete_custom_component(custom_component_id: str, user_id: str):
    try:
        api_context.component_api.delete_custom_component(
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
def save_report(report: ReportSchema, user_id: str):
    try:
        return api_context.report_controller.save(user_id, report)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report")
def list_all_reports(user_id: str):
    try:
        return api_context.report_controller.list_all(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/report/{workflow_id}/{report_id}")
def get_report_by_id(workflow_id: str, report_id: str, user_id: str):
    try:
        return api_context.report_controller.get_by_id(
            user_id, workflow_id, report_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/file/{workflow_id}")
def get_files(
    user_id: str,
    workflow_id: str,
):
    return api_context.file_controller.list_all_workflow_files(
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
def get_component_example(user_id: str, component_label: str):
    eg_workflow = api_context.component_api.get_example_workflow_by_label(
        component_label, user_id
    )

    if eg_workflow is not None:
        api_context.workflow_api.save(user_id, eg_workflow)
    return eg_workflow


@router.post("/component/generate_class_code")
def generate_component_class(user_id: str, component:ComponentModel):
    return get_component_code(component)


@router.post("/component/publish")
def publish_component(user_id: str, component_publishing_input: ComponentPublishingRequestBody):
    api_context.component_api.publish_component(
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
def auto_create_workflow(
    intent: str,
    user_id: str,
):
    try:
        return api_context.workflow_api.auto_create(intent, user_id)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto_workflow_modification")
def auto_modify_workflow(
    workflow: WorkflowModel, modification_instruction: str, user_id: str
):
    return api_context.workflow_api.auto_modify(
        workflow, modification_instruction, user_id
    )



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
def get_datasource(user_id: str, filters: Optional[Dict] = None):
    try:
        dsl = api_context.datasource_controller.get_datasource(user_id, filters)
        return dsl
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasource", response_model=DataSource)
def create_datasource(user_id: str, datasource: Dict = Body(...)):
    try:
        return api_context.datasource_controller.create_datasource(
            user_id, datasource
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/datasource", response_model=DataSource)
def update_datasource(user_id: str, datasource: Dict = Body(...)):
    try:
        return api_context.datasource_controller.update_datasource(
            user_id, datasource
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasource/types")
def get_datasource_types(user_id: str):
    try:
        return DatasourceController.get_datasource_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/datasource/{datasource_id}")
def get_datasource_by_id(user_id: str, datasource_id: str):
    try:
        dsl = api_context.datasource_controller.get_datasource(user_id, {
            "id": datasource_id
        })
        return dsl
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datasource/{datasource_id}")
def delete_datasource(user_id: str, datasource_id: str):
    #try:
        return api_context.datasource_controller.delete_datasource(
            user_id, datasource_id
        )
    #except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasource/{datasource_id}/upload")
def upload_file(
    user_id: str,
    datasource_id: str,
    file: UploadFile = File(...),
):
    try:
        return api_context.datasource_controller.upload_local_file(
            user_id, datasource_id, file
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="There was an error uploading the file: " + str(e),
        )


@router.get("/llm", response_model=List[LLM])
def get_llm(user_id: str, filters: Optional[Dict] = None):
    try:
        return api_context.llm_controller.get_llm(user_id, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm", response_model=LLM)
def create_llm(user_id: str, llm: Dict = Body(...)):
    try:
        return api_context.llm_controller.create_llm(user_id, llm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/llm", response_model=LLM)
def update_llm(user_id: str, llm: Dict = Body(...)):
    try:
        return api_context.llm_controller.update_llm(user_id, llm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/llm/{llm_id}")
def delete_llm(user_id: str, llm_id: str):
    try:
        return api_context.llm_controller.delete_llm(user_id, llm_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm/types")
def get_llm_types():
    try:
        return LLMController.get_llm_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(router)
