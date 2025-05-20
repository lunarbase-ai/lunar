import pytest
from lunarbase.modeling.datasources import DataSourceType
import uuid
from pathlib import Path

class TestDeleteDatasource:
    def test_delete_existing_datasource(self, datasource_repository, config, path_resolver):
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
        result = datasource_repository.delete(user_id, datasource_dict["id"])

        assert result is True
        datasource_path = path_resolver.get_user_datasource_path(datasource_dict["id"], user_id)
        assert not Path(datasource_path).exists()

    def test_delete_nonexistent_datasource_raises_error(self, datasource_repository, config):
        user_id = config.DEFAULT_USER_TEST_PROFILE
        nonexistent_id = str(uuid.uuid4())

        with pytest.raises(ValueError) as exc_info:
            datasource_repository.delete(user_id, nonexistent_id)
        
        assert f"Datasource {nonexistent_id} does not exist!" in str(exc_info.value) 