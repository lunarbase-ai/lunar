from typing import Any

import pytest
from unittest.mock import patch
from lunarcore.component.data_types import DataType
from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.lunar_component import LunarComponent
from lunarcore.data_sources import DataSourceType


# Mocking the DataSourceType and related components

@pytest.fixture
def mock_local_file_connection():
    """Fixture to mock LocalFileConnection."""
    with patch("lunarcore.data_sources.LocalFileConnection", autospec=True) as MockConnection:
        MockConnection.return_value = MockConnection
        MockConnection.file_root = "/mock/path"
        yield MockConnection


class TestLunarComponent:
    def test_init_subclass(self):
        """Test `__init_subclass__` sets class attributes."""

        class MockComponent(
            LunarComponent,
            component_name="MockComponent",
            input_types={"input1": DataType.TEXT},
            data_source_types={"source1": DataSourceType.LOCAL_FILE},
            output_type=DataType.LIST,
        ):
            def run(self, **inputs):
                pass

        assert MockComponent.component_name == "MockComponent"
        assert MockComponent.input_types == {"input1": DataType.TEXT}
        assert MockComponent.data_source_types == {"source1": DataSourceType.LOCAL_FILE}
        assert MockComponent.output_type == DataType.LIST
        assert MockComponent.component_group == ComponentGroup.LUNAR

    def test_init_configuration_and_connections(self, mock_local_file_connection):
        """Test the initialization of a `LunarComponent` instance."""
        class MockComponent(
            LunarComponent,
            component_name="MockComponent",
            input_types={"input1": DataType.TEXT},
            data_source_types={"source1": DataSourceType.LOCAL_FILE},
            output_type=DataType.LIST,
            config_key="default_config",
        ):
            def run(self, **inputs):
                pass

        configuration = {"source1": {"file_root": "/mock/path"}}
        component = MockComponent(configuration=configuration)

        assert component.configuration["source1"]["file_root"] == "/mock/path"
        assert "source1" in component.connections
        assert component.connections["source1"] == mock_local_file_connection.return_value

    @patch("lunarcore.component.lunar_component.LunarComponent._get_connections_from_configuration")
    def test_get_connections(self, mock_get_connections, mock_local_file_connection):
        """Ensure `_get_connections_from_configuration` is called with correct args."""
        class MockComponent(
            LunarComponent,
            component_name="MockComponent",
            input_types={"input1": DataType.TEXT},
            data_source_types={"source1": DataSourceType.LOCAL_FILE},
            output_type=DataType.LIST,
        ):
            def run(self, **inputs):
                pass

        configuration = {"source1": {"file_root": "/mock/path"}}
        mock_get_connections.return_value = {"source1": mock_local_file_connection.return_value}

        component = MockComponent(configuration=configuration)
        mock_get_connections.assert_called_once_with(configuration)
        assert component.connections["source1"] == mock_local_file_connection.return_value

    def test_run_abstract_method(self):
        """Test that a subclass of `LunarComponent` must implement `run`."""

        class InvalidComponent(
            LunarComponent,
            component_name="InvalidComponent",
            input_types={"input1": DataType.TEXT},
            data_source_types={"source1": DataSourceType.LOCAL_FILE},
            output_type=DataType.LIST,
        ):
            def run(self, **inputs: Any):
                pass

        with pytest.raises(TypeError):
            InvalidComponent()
