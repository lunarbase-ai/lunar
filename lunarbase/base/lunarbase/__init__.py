#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from functools import cache

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from lunarbase.agent_copilot import AgentCopilot
from lunarbase.config import lunar_config_factory
from lunarbase.controllers.code_completion_controller import CodeCompletionController
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.controllers.demo_controller import DemoController
from lunarbase.controllers.file_controller import FileController
from lunarbase.controllers.llm_controller import LLMController
from lunarbase.controllers.report_controller import ReportController
from lunarbase.domains.component.api import ComponentAPI
from lunarbase.domains.workflow.api import WorkflowAPI
from lunarbase.domains.workflow.controllers import WorkflowController
from lunarbase.domains.workflow.repositories import LocalFilesWorkflowRepository
from lunarbase.domains.datasources.repositories import LocalFilesDataSourceRepository
from lunarbase.domains.datasources.controllers import DataSourceController
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.orchestration.engine import LunarEngine
from lunarbase.orchestration.prefect_orchestrator import PrefectOrchestrator
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
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.LUNAR_ENGINE,
        LunarEngine,
        name="lunar_engine",
        config=tokens.LUNAR_CONFIG,
        datasource_controller=tokens.DATASOURCE_CONTROLLER,
        orchestrator=tokens.PREFECT_ORCHESTRATOR,
    )

    container.register(
        tokens.PREFECT_ORCHESTRATOR,
        PrefectOrchestrator,
        name="prefect_orchestrator",
        config=tokens.LUNAR_CONFIG,
    )

    container.register(
        tokens.PERSISTENCE_LAYER,
        PersistenceLayer,
        name="persistence_layer",
        config=tokens.LUNAR_CONFIG
    )

    container.register_factory(
        tokens.LLM,
        lambda config: AzureChatOpenAI(
            openai_api_version=config.AZURE_OPENAI_API_VERSION,
            deployment_name=config.AZURE_OPENAI_DEPLOYMENT,
            openai_api_key=config.AZURE_OPENAI_API_KEY,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            model_name=config.AZURE_OPENAI_MODEL_NAME
        ),
        name="llm",
        config=tokens.LUNAR_CONFIG
    )

    container.register_factory(
        tokens.EMBEDDINGS,
        lambda config: AzureOpenAIEmbeddings(
            openai_api_version=config.AZURE_OPENAI_API_VERSION,
            model=config.AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT,    
            openai_api_key=config.AZURE_OPENAI_API_KEY,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        ),
        name="embeddings",
        config=tokens.LUNAR_CONFIG
    )

    container.register_factory(
        tokens.IN_MEMORY_VECTOR_STORE,
        lambda embedding: InMemoryVectorStore(embedding=embedding),
        name="in_memory_vector_store",
        embedding=tokens.EMBEDDINGS
    )
    container.register(
        tokens.AGENT_COPILOT,
        AgentCopilot,
        name="agent_copilot",
        lunar_config=tokens.LUNAR_CONFIG,
        lunar_registry=tokens.LUNAR_REGISTRY,
        llm=tokens.LLM,
        embeddings=tokens.EMBEDDINGS,
        vector_store=tokens.IN_MEMORY_VECTOR_STORE
    )

    container.register(
        tokens.LOCAL_FILES_STORAGE_CONNECTION,
        LocalFilesStorageConnection,
        name="local_files_storage_connection",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.PATH_RESOLVER,
        LocalFilesPathResolver,
        name="path_resolver",
        connection=tokens.LOCAL_FILES_STORAGE_CONNECTION,
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.WORKFLOW_SEARCH_INDEX,
        WorkflowSearchIndex,
        name="workflow_search_index",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.WORKFLOW_REPOSITORY,
        LocalFilesWorkflowRepository,
        name="workflow_repository",
        connection=tokens.LOCAL_FILES_STORAGE_CONNECTION,
        config=tokens.LUNAR_CONFIG,
        persistence_layer=tokens.PERSISTENCE_LAYER,
        path_resolver=tokens.PATH_RESOLVER
    )

    container.register(
        tokens.DATASOURCE_REPOSITORY,
        LocalFilesDataSourceRepository,
        name="datasource_repository",
        connection=tokens.LOCAL_FILES_STORAGE_CONNECTION,
        config=tokens.LUNAR_CONFIG,
        path_resolver=tokens.PATH_RESOLVER
    )

    container.register(
        tokens.WORKFLOW_CONTROLLER,
        WorkflowController,
        name="workflow_controller",
        config=tokens.LUNAR_CONFIG,
        lunar_registry=tokens.LUNAR_REGISTRY,
        lunar_engine=tokens.LUNAR_ENGINE,
        workflow_repository=tokens.WORKFLOW_REPOSITORY,
        agent_copilot=tokens.AGENT_COPILOT,
        workflow_search_index=tokens.WORKFLOW_SEARCH_INDEX,
        persistence_layer=tokens.PERSISTENCE_LAYER,
        path_resolver=tokens.PATH_RESOLVER
    )

    container.register(
        tokens.COMPONENT_CONTROLLER,
        ComponentController,
        name="component_controller",
        config=tokens.LUNAR_CONFIG,
        lunar_registry=tokens.LUNAR_REGISTRY,
        lunar_engine=tokens.LUNAR_ENGINE,
        workflow_repository=tokens.WORKFLOW_REPOSITORY,
    )

    container.register(
        tokens.DEMO_CONTROLLER,
        DemoController,
        name="demo_controller",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.REPORT_CONTROLLER,
        ReportController,
        name="report_controller",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.FILE_CONTROLLER,
        FileController,
        name="file_controller",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.CODE_COMPLETION_CONTROLLER,
        CodeCompletionController,
        name="code_completion_controller",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.DATASOURCE_CONTROLLER,
        DataSourceController,
        name="datasource_controller",
        config=tokens.LUNAR_CONFIG,
        datasource_repository=tokens.DATASOURCE_REPOSITORY,
        file_storage_connection=tokens.LOCAL_FILES_STORAGE_CONNECTION,
        file_path_resolver=tokens.PATH_RESOLVER
    )

    container.register(
        tokens.LLM_CONTROLLER,
        LLMController,
        name="llm_controller",
        config=tokens.LUNAR_CONFIG
    )

    container.register(
        tokens.COMPONENT_API,
        ComponentAPI,
        name="component_api",
        component_controller=tokens.COMPONENT_CONTROLLER
    )

    container.register(
        tokens.WORKFLOW_API,
        WorkflowAPI,
        name="workflow_api",
        workflow_controller=tokens.WORKFLOW_CONTROLLER
    )

    return container