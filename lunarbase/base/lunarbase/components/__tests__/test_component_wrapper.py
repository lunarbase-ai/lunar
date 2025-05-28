#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import os
import pytest
from unittest.mock import Mock, patch, create_autospec
from lunarbase.components.component_wrapper import ComponentWrapper
from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
    UNDEFINED
)
from lunarcore.component.data_types import DataType
from lunarcore.component.lunar_component import LunarComponent
from lunarcore.component.component_group import ComponentGroup
from lunarbase.config import ENVIRONMENT_PREFIX
from lunarbase.components.system_component import SystemComponent

class MockComponent(
    LunarComponent,
    component_name="TestComponent",
    component_description="Test description",
    input_types={
        "input1": DataType.TEXT,
        "input2": DataType.TEXT
    },
    output_type=DataType.ANY,
    component_group=ComponentGroup.UTILS
):
    def __init__(self, configuration=None):
        super().__init__(configuration=configuration)
    
    @classmethod
    def create(cls, **kwargs):
        return cls(configuration=kwargs)
    
    def run(self, **kwargs):
        return kwargs

class MockSystemComponent(
    SystemComponent,
    component_name="TestSystemComponent",
    component_description="Test system component",
    input_types={
        "input1": DataType.TEXT,
        "input2": DataType.TEXT
    },
    output_type=DataType.ANY,
    component_group=ComponentGroup.UTILS
):
    def resolve_deps(self, container):
        return {}
    def __init__(self, deps: dict, **kwargs):
        super().__init__(deps=deps, **kwargs)
        self.container = kwargs.get('container')
    @classmethod
    def create(cls, container, **kwargs):
        return cls(deps={}, container=container, **kwargs)
    def run(self, **kwargs):
        return kwargs

class TestComponentWrapper:
    @pytest.fixture
    def mock_registry(self):
        registry = Mock()
        mock_component_model = ComponentModel(
            id="test_id",
            workflow_id="workflow_1",
            name="TestComponent",
            class_name="MockComponent",
            label="Test Label",
            description="Test description",
            group="test_group",
            inputs=[],
            output=ComponentOutput(data_type=DataType.ANY),
            is_terminal=False
        )
        
        registry.get_by_class_name.return_value = Mock(
            module_name="test_module",
            component_model=mock_component_model
        )
        return registry

    @pytest.fixture
    def mock_container(self):
        return Mock()

    @pytest.fixture
    def basic_component_model(self):
        return ComponentModel(
            id="test_id",
            workflow_id="workflow_1",
            name="TestComponent",
            class_name="MockComponent",
            label="Test Label",
            description="Test description",
            group="test_group",
            inputs=[],
            output=ComponentOutput(data_type=DataType.ANY),
            is_terminal=False
        )

    def test_component_initialization(self, mock_registry, mock_container, basic_component_model):
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            assert wrapper.component_model.name == "TestComponent"
            assert wrapper.component_model.class_name == "MockComponent"

    def test_system_component_initialization(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.class_name = "MockSystemComponent"
        basic_component_model.name = "TestSystemComponent"
        
        mock_module = Mock()
        mock_module.MockSystemComponent = MockSystemComponent
        
        mock_registry.get_by_class_name.return_value = Mock(
            module_name="test_module",
            component_model=ComponentModel(
                id="test_id",
                workflow_id="workflow_1",
                name="TestSystemComponent",
                class_name="MockSystemComponent",
                label="Test Label",
                description="Test system component",
                group="test_group",
                inputs=[],
                output=ComponentOutput(data_type=DataType.ANY),
                is_terminal=False
            )
        )
        
        with patch('importlib.import_module', return_value=mock_module):
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            assert wrapper.component_model.name == "TestSystemComponent"
            assert wrapper.component_model.class_name == "MockSystemComponent"

            assert wrapper.component_instance.container == mock_container

    def test_environment_variable_resolution(self, mock_registry, mock_container, basic_component_model):
        os.environ['TEST_VAR'] = 'test_value'
        
        basic_component_model.configuration = {
            'test_key': f'{ENVIRONMENT_PREFIX}TEST_VAR'
        }
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            assert wrapper.configuration['test_key'] == 'test_value'

    def test_missing_environment_variable(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.configuration = {
            'test_key': f'{ENVIRONMENT_PREFIX}NONEXISTENT_VAR'
        }
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            with pytest.raises(Exception) as exc_info:
                ComponentWrapper(
                    component=basic_component_model,
                    lunar_registry=mock_registry,
                    container=mock_container
                )
            
            assert "Expected environment variable" in str(exc_info.value)

    def test_component_run_with_single_input(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.inputs = [
            ComponentInput(key="input1", data_type=DataType.TEXT, value="test")
        ]
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            result = wrapper.run_in_workflow()
            assert result.output.value == {"input1": "test"}

    def test_component_run_with_mapped_inputs(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.inputs = [
            ComponentInput(key="input1", data_type=DataType.TEXT, value=["test1", "test2"]),
            ComponentInput(key="input2", data_type=DataType.TEXT, value="static")
        ]
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            result = wrapper.run_in_workflow()
            assert len(result.output.value) == 2
            assert result.output.value[0]["input1"] == "test1"
            assert result.output.value[1]["input1"] == "test2"

    def test_component_run_with_undefined_input(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.inputs = [
            ComponentInput(key="input1", data_type=DataType.TEXT, value=UNDEFINED)
        ]
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            result = wrapper.run_in_workflow()
            assert result.output.value == {"input1": None}

    def test_component_run_with_template_variables(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.inputs = [
            ComponentInput(
                key="input1",
                data_type=DataType.TEMPLATE,
                value="Hello, {name}!",
                template_variables={"input1.name": "test_value"}
            )
        ]
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            result = wrapper.run_in_workflow()
            assert result.output.value == {"input1": "Hello, test_value!"}

    def test_invalid_component_class(self, mock_registry, mock_container, basic_component_model):
        mock_registry.get_by_class_name.return_value = None
        
        with pytest.raises(Exception) as exc_info:
            ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
        
        assert "Component not found" in str(exc_info.value)

    def test_invalid_input_key(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.inputs = [
            ComponentInput(key="nonexistent_input", data_type=DataType.TEXT, value="test")
        ]
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            with pytest.raises(Exception) as exc_info:
                wrapper.run_in_workflow()
            
            assert "Unexpected input" in str(exc_info.value)

    def test_force_run_configuration(self, mock_registry, mock_container, basic_component_model):
        basic_component_model.configuration = {
            "force_run": True
        }
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock(MockComponent=MockComponent)
            
            wrapper = ComponentWrapper(
                component=basic_component_model,
                lunar_registry=mock_registry,
                container=mock_container
            )
            
            assert wrapper.disable_cache is True