from dataclasses import dataclass
from functools import cache
from pathlib import Path
from lunarbase.config import LunarConfig
from lunarbase.registry import LunarRegistry
from lunarbase.persistence import PersistenceLayer
from lunarbase.controllers.workflow_controller import WorkflowController
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.domains.component.api import ComponentAPI
from lunarbase.domains.workflow.api import WorkflowAPI
from lunarbase.controllers.demo_controller import DemoController
from lunarbase.controllers.report_controller import ReportController
from lunarbase.controllers.file_controller import FileController
from lunarbase.controllers.code_completion_controller import CodeCompletionController
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.llm_controller import LLMController

@cache
def lunar_context_factory() -> "LunarContext":
    lunar_config = None
    if Path(LunarConfig.DEFAULT_ENV).is_file():
        lunar_config = LunarConfig.get_config(
            settings_file_path=LunarConfig.DEFAULT_ENV
        )
    if lunar_config is None:
        raise FileNotFoundError(LunarConfig.DEFAULT_ENV)

    lunar_registry = LunarRegistry(config=lunar_config)


    workflow_controller=WorkflowController(
            config=lunar_config,
            lunar_registry=lunar_registry,
        )
    component_controller=ComponentController(config=lunar_config, lunar_registry=lunar_registry)
    demo_controller=DemoController(config=lunar_config)
    report_controller=ReportController(config=lunar_config)
    file_controller=FileController(config=lunar_config)
    code_completion_controller=CodeCompletionController(config=lunar_config)
    datasource_controller=DatasourceController(config=lunar_config)
    llm_controller=LLMController(config=lunar_config)

    component_api=ComponentAPI(component_controller=component_controller)
    workflow_api=WorkflowAPI(workflow_controller=workflow_controller)

    persistence_layer=PersistenceLayer(config=lunar_config)

    return LunarContext(
        lunar_config=lunar_config,
        lunar_registry=lunar_registry,

        workflow_controller=workflow_controller,
        component_controller=component_controller,
        demo_controller=demo_controller,
        report_controller=report_controller,
        file_controller=file_controller,
        code_completion_controller=code_completion_controller,
        datasource_controller=datasource_controller,
        llm_controller=llm_controller,

        component_api=component_api,
        workflow_api=workflow_api,

        persistence_layer=persistence_layer,
    )

@dataclass
class LunarContext:
    lunar_config: LunarConfig
    lunar_registry: LunarRegistry

    workflow_controller: WorkflowController
    component_controller: ComponentController

    component_api: ComponentAPI
    workflow_api: WorkflowAPI
    demo_controller: DemoController
    report_controller: ReportController
    file_controller: FileController
    code_completion_controller: CodeCompletionController
    datasource_controller: DatasourceController
    llm_controller: LLMController

    persistence_layer: PersistenceLayer