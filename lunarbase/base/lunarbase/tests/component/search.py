import pytest
from lunarbase import LUNAR_CONTEXT
from lunarbase.controllers.component_controller import ComponentController

@pytest.fixture
def controller():
    return ComponentController(LUNAR_CONTEXT.lunar_registry.config)

def test_search(controller):
    search_query = 'Azure OpenAI'
    expected_name = 'Azure Open AI prompt'

    components = controller.search(search_query, 'admin')

    assert components, "Expected at least one result, but got none."
    assert components[0].name == expected_name, f"Expected '{expected_name}', but got '{components[0].name}'"
