import pytest
from lunarbase.modeling.datasources import DataSourceType
import uuid

class TestShowDatasource:
    def test_show_datasource_returns_datasource(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        datasource_dict = {
            "id": str(uuid.uuid4()),
            "name": "Test Datasource",
            "description": "Test Datasource",
            "type": DataSourceType.LOCAL_FILE,
            "connection_attributes": {
                "files": []
            }
        }

        datasource_repository.create(user_id, datasource_dict)

        retrieved_datasource = datasource_repository.show(user_id, datasource_dict["id"])

        assert retrieved_datasource.id == datasource_dict["id"]
        assert retrieved_datasource.name == datasource_dict["name"]
        assert retrieved_datasource.description == datasource_dict["description"]
        assert retrieved_datasource.type == datasource_dict["type"]
        assert retrieved_datasource.connection_attributes.model_dump() == datasource_dict["connection_attributes"]

    def test_show_nonexistent_datasource_raises_error(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        nonexistent_id = str(uuid.uuid4())

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.show(user_id, nonexistent_id)
        
        assert f"Datasource {nonexistent_id} does not exist!" in str(exc_info.value) 