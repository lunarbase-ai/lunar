import pytest
from lunarbase.modeling.datasources import DataSourceType


class TestIndexTypes:
    def test_index_types_returns_expected_types(self, mock_datasource_controller):
        result = mock_datasource_controller.index_types()

        assert isinstance(result, list)
        for e in DataSourceType:
            found = any(
                item["id"] == e.name and
                item["name"] == e.name.replace("_", " ") and
                item["connectionAttributes"] == e.expected_connection_attributes()[1]
                for item in result
            )
            assert found, f"Type {e.name} not found in result" 