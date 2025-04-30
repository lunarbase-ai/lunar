from pathlib import Path

import pytest
from fastapi import UploadFile

from lunarbase import LUNAR_CONTEXT
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.controllers.datasource_controller import DatasourceController
from lunarbase.controllers.workflow_controller import WorkflowController



@pytest.fixture(scope="function", autouse=True)
def startup():
    LUNAR_CONTEXT.lunar_registry.persistence_layer.init_user_profile(
        LUNAR_CONTEXT.lunar_config.DEFAULT_USER_TEST_PROFILE
    )

    yield

    LUNAR_CONTEXT.lunar_registry.persistence_layer.delete_user_profile(
        LUNAR_CONTEXT.lunar_config.DEFAULT_USER_TEST_PROFILE
    )

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

@pytest.fixture
def empty_local_file_datasource(datasource_controller):
    datasource = datasource_controller.create_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_PROFILE,
        datasource={
            "name": "Local file test datasource",
            "type": "LOCAL_FILE",
            "connection_attributes": {"file_name": "empty_file.txt"},
        },
    )
    yield datasource

    datasource_controller.delete_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_PROFILE,
        datasource_id=datasource.id,
    )
