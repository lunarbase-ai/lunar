import pytest

@pytest.fixture(autouse=True)
def setup_integration_test_environment(lunar_context):
    lunar_context.lunar_registry.load_cached_components()
    lunar_context.lunar_registry.register()