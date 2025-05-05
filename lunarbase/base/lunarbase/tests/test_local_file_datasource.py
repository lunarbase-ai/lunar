from pathlib import Path
import pytest
from lunarbase import LUNAR_CONTEXT
from fastapi import UploadFile
import logging

logging.basicConfig(level=logging.INFO)

@pytest.fixture
def datasource(datasource_controller):
    datasource = datasource_controller.create_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_TEST_PROFILE,
        datasource={
            "name": "Local file test datasource",
            "type": "LOCAL_FILE",
            'connectionAttributes': {}
        },
    )

    yield datasource

    datasource_controller.delete_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_TEST_PROFILE,
        datasource_id=datasource.id,
    )

@pytest.fixture 
def uploaded_local_text_file():
    filename = "lunar_uploaded_file_fixture.txt"
    basepath = LUNAR_CONTEXT.lunar_registry.persistence_layer.get_user_file_root(
        LUNAR_CONTEXT.lunar_config.DEFAULT_USER_TEST_PROFILE
    )
    filepath = Path(basepath, filename)
    with open(filepath, "w") as f:
        f.write("LUNAR")
    yield UploadFile(file=filepath.open("rb"), filename=filename)

    Path.unlink(filepath, missing_ok=True)


@pytest.mark.usefixtures("datasource")
def test_local_datasources_can_be_created(datasource_controller):
    user_datasources = datasource_controller.get_datasource(
        user_id=datasource_controller.config.DEFAULT_USER_TEST_PROFILE
    )

    assert len(user_datasources) == 1

def test_local_files_can_be_uploaded(datasource_controller, datasource, uploaded_local_text_file):
    datasource_controller.upload_local_file(
        user_id=datasource_controller.config.DEFAULT_USER_TEST_PROFILE,
        datasource_id=datasource.id,
        file=uploaded_local_text_file
    )

    datasource = datasource_controller.get_datasource(datasource_controller.config.DEFAULT_USER_TEST_PROFILE, {
            "id": datasource.id
    })[0]

    assert len(datasource.connection_attributes.files) == 1