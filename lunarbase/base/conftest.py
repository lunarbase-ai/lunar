import pytest

from lunarbase import lunar_context_factory

@pytest.fixture(scope="session")
def lunar_context():
    return lunar_context_factory()

@pytest.fixture
def config(lunar_context):
    return lunar_context.lunar_config

@pytest.fixture(scope="function", autouse=True)
def startup(lunar_context):
    lunar_context.persistence_layer.init_user_profile(
        lunar_context.lunar_config.DEFAULT_USER_TEST_PROFILE
    )

    yield

    lunar_context.persistence_layer.delete_user_profile(
        lunar_context.lunar_config.DEFAULT_USER_TEST_PROFILE
    )

@pytest.fixture
def registry(lunar_context):
    return lunar_context.lunar_registry

@pytest.fixture
def workflow_controller(lunar_context):
    return lunar_context.workflow_controller


@pytest.fixture
def component_controller(lunar_context):
    return lunar_context.component_controller


@pytest.fixture
def datasource_controller(lunar_context):
    return lunar_context.datasource_controller
 

@pytest.fixture
def sparql_datasource(datasource_controller):
    datasource = datasource_controller.create_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_PROFILE,
        datasource={
            "name": "SPARQL test datasource",
            "type": "SPARQL",
            "connection_attributes": {"endpoint": "http://dbpedia.org/sparql"},
        },
    )
    yield datasource

    datasource_controller.delete_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_PROFILE,
        datasource_id=datasource.id,
    )

