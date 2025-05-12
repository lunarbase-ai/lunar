from dataclasses import dataclass
from functools import cache
from pathlib import Path

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from lunarbase.agent_copilot import AgentCopilot
from lunarbase.config import lunar_config_factory, LunarConfig
from lunarbase.controllers.code_completion_controller import CodeCompletionController
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.demo_controller import DemoController
from lunarbase.controllers.file_controller import FileController
from lunarbase.controllers.llm_controller import LLMController
from lunarbase.controllers.report_controller import ReportController
from lunarbase.domains.component.api import ComponentAPI
from lunarbase.domains.workflow.api import WorkflowAPI
from lunarbase.domains.workflow.controllers import WorkflowController
from lunarbase.domains.workflow.repositories import LocalFilesWorkflowRepository, WorkflowRepository
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.persistence import PersistenceLayer
from lunarbase.persistence.connections import LocalFilesStorageConnection
from lunarbase.persistence.resolvers import LocalFilesPathResolver
from lunarbase.registry import LunarRegistry

from lunarbase.ioc import tokens
from lunarbase.ioc.container import LunarContainer

@cache
def lunar_context_factory() -> "LunarContainer":
    lunar_container = LunarContainer()

    lunar_container.register(tokens.LUNAR_CONFIG, lunar_config_factory(),"lunar_config")
    lunar_container.register(tokens.LUNAR_REGISTRY, LunarRegistry(config=lunar_container.get(tokens.LUNAR_CONFIG)),"lunar_registry")
    lunar_container.register(tokens.PERSISTENCE_LAYER, PersistenceLayer(config=lunar_container.get(tokens.LUNAR_CONFIG)),"persistence_layer")


    # SERVICES
    lunar_container.register(tokens.LLM, AzureChatOpenAI(
        openai_api_version=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_VERSION,
        deployment_name=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_DEPLOYMENT,
        openai_api_key=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_KEY,
        azure_endpoint=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_ENDPOINT,
        model_name=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_MODEL_NAME,
    ),"llm")
    lunar_container.register(tokens.EMBEDDINGS, AzureOpenAIEmbeddings(
        openai_api_version=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_VERSION,
        deployment_name=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT,
        openai_api_key=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_KEY,
        azure_endpoint=lunar_container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_ENDPOINT,
    ),"embeddings")

    lunar_container.register(tokens.AGENT_COPILOT, AgentCopilot(
        lunar_config=lunar_container.get(tokens.LUNAR_CONFIG),
        lunar_registry=lunar_container.get(tokens.LUNAR_REGISTRY),
        llm=lunar_container.get(tokens.LLM),
        embeddings=lunar_container.get(tokens.EMBEDDINGS),
        vector_store=InMemoryVectorStore,
    ),"agent_copilot")

    # STORAGE CONNECTIONS
    lunar_container.register(
        tokens.LOCAL_FILES_STORAGE_CONNECTION, 
        LocalFilesStorageConnection(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "local_files_storage_connection"
    )

    # PATH RESOLVER
    lunar_container.register(
        tokens.PATH_RESOLVER, 
        LocalFilesPathResolver(
            lunar_container.get(tokens.LOCAL_FILES_STORAGE_CONNECTION), 
            lunar_container.get(tokens.LUNAR_CONFIG)
        ),
        "path_resolver"
    )

    # INDEXES 
    lunar_container.register(
        tokens.WORKFLOW_SEARCH_INDEX, 
        WorkflowSearchIndex(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "workflow_search_index"
    )

    # REPOSITORIES
    lunar_container.register(
        tokens.WORKFLOW_REPOSITORY, 
        LocalFilesWorkflowRepository(
            connection = lunar_container.get(tokens.LOCAL_FILES_STORAGE_CONNECTION),
            config = lunar_container.get(tokens.LUNAR_CONFIG),
            persistence_layer=lunar_container.get(tokens.PERSISTENCE_LAYER),
            path_resolver=lunar_container.get(tokens.PATH_RESOLVER)
        ),
        "workflow_repository"
    )

    # CONTROLLERS
    lunar_container.register(
        tokens.WORKFLOW_CONTROLLER, 
        WorkflowController(
            config=lunar_container.get(tokens.LUNAR_CONFIG),
            lunar_registry=lunar_container.get(tokens.LUNAR_REGISTRY),
            workflow_repository=lunar_container.get(tokens.WORKFLOW_REPOSITORY),
            agent_copilot=lunar_container.get(tokens.AGENT_COPILOT),
            workflow_search_index=lunar_container.get(tokens.WORKFLOW_SEARCH_INDEX),
            persistence_layer=lunar_container.get(tokens.PERSISTENCE_LAYER),
            path_resolver=lunar_container.get(tokens.PATH_RESOLVER)
        ),
        "workflow_controller"
    )

    lunar_container.register(
        tokens.COMPONENT_CONTROLLER, 
        ComponentController(
            config=lunar_container.get(tokens.LUNAR_CONFIG), 
            lunar_registry=lunar_container.get(tokens.LUNAR_REGISTRY)
        ),
        "component_controller"
    )
    lunar_container.register(
        tokens.DEMO_CONTROLLER, 
        DemoController(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "demo_controller"
    )
    lunar_container.register(
        tokens.REPORT_CONTROLLER, 
        ReportController(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "report_controller"
    )
    lunar_container.register(
        tokens.FILE_CONTROLLER, 
        FileController(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "file_controller"
    )
    lunar_container.register(
        tokens.CODE_COMPLETION_CONTROLLER, 
        CodeCompletionController(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "code_completion_controller"
    )
    lunar_container.register(
        tokens.DATASOURCE_CONTROLLER, 
        DatasourceController(
            config=lunar_container.get(tokens.LUNAR_CONFIG), 
            persistence_layer=lunar_container.get(tokens.PERSISTENCE_LAYER)
        ),
        "datasource_controller"
    )
    lunar_container.register(
        tokens.LLM_CONTROLLER, 
        LLMController(config=lunar_container.get(tokens.LUNAR_CONFIG)),
        "llm_controller"
    )

    # API
    lunar_container.register(
        tokens.COMPONENT_API, 
        ComponentAPI(component_controller=lunar_container.get(tokens.COMPONENT_CONTROLLER)),
        "component_api"
    )
    lunar_container.register(
        tokens.WORKFLOW_API, 
        WorkflowAPI(workflow_controller=lunar_container.get(tokens.WORKFLOW_CONTROLLER)),
        "workflow_api"
    )

    return lunar_container