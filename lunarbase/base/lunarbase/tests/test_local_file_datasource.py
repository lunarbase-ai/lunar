from pathlib import Path

import pytest

@pytest.mark.asyncio
async def test_datasource(local_file_datasource, datasource_controller):
    file = local_file_datasource.to_component_input(
        base_path=datasource_controller.persistence_layer.get_user_file_root(
            datasource_controller.config.DEFAULT_USER_PROFILE
        )
    )
    assert Path(file.path).exists()
    with open(file.path, "r") as f:
        assert f.read() == "LUNAR"
