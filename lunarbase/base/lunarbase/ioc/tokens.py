#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from lunarbase.agent_copilot import AgentCopilot
from lunarbase.config import LunarConfig
from lunarbase.controllers.code_completion_controller import CodeCompletionController
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.demo_controller import DemoController
from lunarbase.controllers.file_controller import FileController
from lunarbase.controllers.llm_controller import LLMController
from lunarbase.controllers.report_controller import ReportController
from lunarbase.domains.component.api import ComponentAPI
from lunarbase.domains.datasources.repositories import DatasourceRepository
from lunarbase.domains.workflow.api import WorkflowAPI
from lunarbase.domains.workflow.controllers import WorkflowController
from lunarbase.domains.workflow.repositories import WorkflowRepository
from lunarbase.indexing.workflow_search_index import WorkflowSearchIndex
from lunarbase.orchestration.prefect_orchestrator import PrefectOrchestrator
from lunarbase.persistence import PersistenceLayer
from lunarbase.persistence.connections import LocalFilesStorageConnection
from lunarbase.persistence.resolvers import LocalFilesPathResolver
from lunarbase.registry import LunarRegistry
from lunarbase.orchestration.engine import LunarEngine

from typing import TypeVar, Generic, Type

T = TypeVar('T')

class ServiceToken(Generic[T]):
    def __init__(self, service_type: Type[T]):
        self.service_type = service_type

LUNAR_CONFIG = ServiceToken(LunarConfig)
LUNAR_REGISTRY = ServiceToken(LunarRegistry)
LUNAR_ENGINE = ServiceToken(LunarEngine)
PREFECT_ORCHESTRATOR = ServiceToken(PrefectOrchestrator)
PERSISTENCE_LAYER = ServiceToken(PersistenceLayer)
LLM = ServiceToken(AzureChatOpenAI)
IN_MEMORY_VECTOR_STORE = ServiceToken(InMemoryVectorStore)
EMBEDDINGS = ServiceToken(AzureOpenAIEmbeddings)
AGENT_COPILOT = ServiceToken(AgentCopilot)
LOCAL_FILES_STORAGE_CONNECTION = ServiceToken(LocalFilesStorageConnection)
PATH_RESOLVER = ServiceToken(LocalFilesPathResolver)
WORKFLOW_SEARCH_INDEX = ServiceToken(WorkflowSearchIndex)

WORKFLOW_REPOSITORY = ServiceToken(WorkflowRepository)
DATASOURCE_REPOSITORY = ServiceToken(DatasourceRepository)

WORKFLOW_CONTROLLER = ServiceToken(WorkflowController)
COMPONENT_CONTROLLER = ServiceToken(ComponentController)
DEMO_CONTROLLER = ServiceToken(DemoController)
REPORT_CONTROLLER = ServiceToken(ReportController)
FILE_CONTROLLER = ServiceToken(FileController)
CODE_COMPLETION_CONTROLLER = ServiceToken(CodeCompletionController)
DATASOURCE_CONTROLLER = ServiceToken(DatasourceController)
LLM_CONTROLLER = ServiceToken(LLMController)

COMPONENT_API = ServiceToken(ComponentAPI)
WORKFLOW_API = ServiceToken(WorkflowAPI)