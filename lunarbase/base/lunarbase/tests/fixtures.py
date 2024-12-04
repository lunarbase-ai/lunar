
import pytest
from fastapi import File

from lunarbase import LUNAR_CONTEXT
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.workflow_controller import WorkflowController

@pytest.fixture
def workflow_controller():
    return WorkflowController(config=LUNAR_CONTEXT.lunar_config)

@pytest.fixture
def component_controller():
    return ComponentController(config=LUNAR_CONTEXT.lunar_config)

@pytest.fixture
def datasource_controller():
    return DatasourceController(config=LUNAR_CONTEXT.lunar_config)

@pytest.fixture
def test_file():
    file = File(

    )