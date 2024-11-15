
import pytest

from lunarbase import LUNAR_CONTEXT
from lunarbase.controllers.workflow_controller import WorkflowController

@pytest.fixture
def workflow_controller():
    return WorkflowController(config=LUNAR_CONTEXT.lunar_config)
