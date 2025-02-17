from pathlib import Path

import pytest
from fastapi import UploadFile

from lunarbase import LUNAR_CONTEXT
from lunarbase.controllers.component_controller import ComponentController
from lunarbase.controllers.configuration_profile_controller import ConfigurationProfileController
from lunarbase.controllers.workflow_controller import WorkflowController


@pytest.fixture
def workflow_controller():
    return WorkflowController(config=LUNAR_CONTEXT.lunar_config)


@pytest.fixture
def component_controller():
    return ComponentController(config=LUNAR_CONTEXT.lunar_config)


@pytest.fixture
def uploaded_text_file():
    filename = "lunar_uploaded_file_fixture.txt"
    basepath = LUNAR_CONTEXT.lunar_registry.persistence_layer.get_user_file_root(
        LUNAR_CONTEXT.lunar_config.DEFAULT_USER_PROFILE
    )
    filepath = Path(basepath, filename)
    with open(filepath, "w") as f:
        f.write("LUNAR")

    yield UploadFile(file=filepath.open("rb"), filename=filename)

    Path.unlink(filepath, missing_ok=True)


@pytest.fixture
def configuration_profile_controller():
    return ConfigurationProfileController(config=LUNAR_CONTEXT.lunar_config)


@pytest.fixture
def local_file_datasource(datasource_controller, uploaded_text_file):
    datasource = datasource_controller.create_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_PROFILE,
        datasource={
            "name": "Local file test datasource",
            "type": "LOCAL_FILE",
            "connection_attributes": {"file_name": uploaded_text_file.filename},
        },
    )
    yield datasource

    datasource_controller.delete_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_PROFILE,
        datasource_id=datasource.id,
    )

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
