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
    container = LunarContainer()

    container.register_instance(
        tokens.LUNAR_CONFIG,
        lunar_config_factory(),
        name="lunar_config"
    )

    container.register(
        tokens.LUNAR_REGISTRY,
        LunarRegistry,
        name="lunar_registry",
        config=container.get(tokens.LUNAR_CONFIG)
    )
    

    container.register(
        tokens.PERSISTENCE_LAYER,
        PersistenceLayer,
        name="persistence_layer",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    # Register services
    container.register(
        tokens.LLM,
        AzureChatOpenAI,
        name="llm",
        openai_api_version=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_VERSION,
        deployment_name=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_DEPLOYMENT,
        openai_api_key=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_KEY,
        azure_endpoint=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_ENDPOINT,
        model_name=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_MODEL_NAME
    )

    container.register(
        tokens.EMBEDDINGS,
        AzureOpenAIEmbeddings,
        name="embeddings",
        openai_api_version=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_VERSION,
        deployment_name=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT,
        openai_api_key=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_API_KEY,
        azure_endpoint=container.get(tokens.LUNAR_CONFIG).AZURE_OPENAI_ENDPOINT
    )

    container.register(
        tokens.AGENT_COPILOT,
        AgentCopilot,
        name="agent_copilot",
        lunar_config=container.get(tokens.LUNAR_CONFIG),
        lunar_registry=container.get(tokens.LUNAR_REGISTRY),
        llm=container.get(tokens.LLM),
        embeddings=container.get(tokens.EMBEDDINGS),
        vector_store=InMemoryVectorStore
    )

    # Register storage connections
    container.register(
        tokens.LOCAL_FILES_STORAGE_CONNECTION,
        LocalFilesStorageConnection,
        name="local_files_storage_connection",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    # Register path resolver
    container.register(
        tokens.PATH_RESOLVER,
        LocalFilesPathResolver,
        name="path_resolver",
        connection=container.get(tokens.LOCAL_FILES_STORAGE_CONNECTION),
        config=container.get(tokens.LUNAR_CONFIG)
    )

    # Register indexes
    container.register(
        tokens.WORKFLOW_SEARCH_INDEX,
        WorkflowSearchIndex,
        name="workflow_search_index",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    # Register repositories
    container.register(
        tokens.WORKFLOW_REPOSITORY,
        LocalFilesWorkflowRepository,
        name="workflow_repository",
        connection=container.get(tokens.LOCAL_FILES_STORAGE_CONNECTION),
        config=container.get(tokens.LUNAR_CONFIG),
        persistence_layer=container.get(tokens.PERSISTENCE_LAYER),
        path_resolver=container.get(tokens.PATH_RESOLVER)
    )

    # Register controllers
    container.register(
        tokens.WORKFLOW_CONTROLLER,
        WorkflowController,
        name="workflow_controller",
        config=container.get(tokens.LUNAR_CONFIG),
        lunar_registry=container.get(tokens.LUNAR_REGISTRY),
        workflow_repository=container.get(tokens.WORKFLOW_REPOSITORY),
        agent_copilot=container.get(tokens.AGENT_COPILOT),
        workflow_search_index=container.get(tokens.WORKFLOW_SEARCH_INDEX),
        persistence_layer=container.get(tokens.PERSISTENCE_LAYER),
        path_resolver=container.get(tokens.PATH_RESOLVER)
    )

    container.register(
        tokens.COMPONENT_CONTROLLER,
        ComponentController,
        name="component_controller",
        config=container.get(tokens.LUNAR_CONFIG),
        lunar_registry=container.get(tokens.LUNAR_REGISTRY)
    )

    container.register(
        tokens.DEMO_CONTROLLER,
        DemoController,
        name="demo_controller",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    container.register(
        tokens.REPORT_CONTROLLER,
        ReportController,
        name="report_controller",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    container.register(
        tokens.FILE_CONTROLLER,
        FileController,
        name="file_controller",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    container.register(
        tokens.CODE_COMPLETION_CONTROLLER,
        CodeCompletionController,
        name="code_completion_controller",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    container.register(
        tokens.DATASOURCE_CONTROLLER,
        DatasourceController,
        name="datasource_controller",
        config=container.get(tokens.LUNAR_CONFIG),
        persistence_layer=container.get(tokens.PERSISTENCE_LAYER)
    )

    container.register(
        tokens.LLM_CONTROLLER,
        LLMController,
        name="llm_controller",
        config=container.get(tokens.LUNAR_CONFIG)
    )

    # Register APIs
    container.register(
        tokens.COMPONENT_API,
        ComponentAPI,
        name="component_api",
        component_controller=container.get(tokens.COMPONENT_CONTROLLER)
    )

    container.register(
        tokens.WORKFLOW_API,
        WorkflowAPI,
        name="workflow_api",
        workflow_controller=container.get(tokens.WORKFLOW_CONTROLLER)
    )

    return container