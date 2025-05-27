import pytest
from unittest.mock import Mock
from lunarbase.components.file_datasource import FileDatasource
from lunarbase.domains.datasources.models import DataSourceType, LocalFileConnectionAttributes, LocalFile

@pytest.fixture
def mock_user_context():
    user_context = Mock()
    user_context.user = Mock()
    user_context.user.id = "test-user-id"
    return user_context

@pytest.fixture
def mock_datasource_controller():
    controller = Mock()
    return controller

@pytest.fixture
def mock_container(mock_datasource_controller, mock_user_context):
    container = Mock()
    container.datasource_controller = mock_datasource_controller
    container.user_context = mock_user_context
    return container

@pytest.fixture
def file_datasource(mock_container):
    deps = {
        "datasource_controller": mock_container.datasource_controller,
        "user_context": mock_container.user_context
    }
    return FileDatasource(deps=deps)

def test_resolve_deps(mock_container):
    component = FileDatasource(deps={})
    deps = component.resolve_deps(mock_container)
    
    assert deps["datasource_controller"] == mock_container.datasource_controller
    assert deps["user_context"] == mock_container.user_context

def test_run_successful(file_datasource, mock_datasource_controller, mock_user_context):
    mock_files = [
        LocalFile(file_name="test1.txt"),
        LocalFile(file_name="test2.txt")
    ]
    mock_ds = Mock()
    mock_ds.type = DataSourceType.LOCAL_FILE
    mock_ds.connection_attributes = LocalFileConnectionAttributes(files=mock_files)
    
    mock_datasource_controller.show.return_value = mock_ds
    
    result = file_datasource.run("test-datasource-id")
    
    assert result == ["test1.txt", "test2.txt"]
    mock_datasource_controller.show.assert_called_once_with(
        mock_user_context.user.id,
        "test-datasource-id"
    )

def test_run_missing_controller():
    deps = {
        "datasource_controller": None,
        "user_context": Mock()
    }
    component = FileDatasource(deps=deps)
    
    with pytest.raises(Exception, match="Failed accessing datasource controller"):
        component.run("test-datasource-id")

def test_run_missing_user(mock_datasource_controller):
    deps = {
        "datasource_controller": mock_datasource_controller,
        "user_context": Mock()
    }
    deps["user_context"].user = None
    component = FileDatasource(deps=deps)
    
    with pytest.raises(Exception, match="No user found in context"):
        component.run("test-datasource-id")

def test_run_wrong_datasource_type(file_datasource, mock_datasource_controller):
    mock_ds = Mock()
    mock_ds.type = DataSourceType.POSTGRESQL
    mock_datasource_controller.show.return_value = mock_ds
    
    with pytest.raises(Exception, match="Datasource is not a local file datasource"):
        file_datasource.run("test-datasource-id") 