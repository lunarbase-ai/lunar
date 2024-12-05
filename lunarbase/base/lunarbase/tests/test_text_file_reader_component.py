from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
)


@pytest.mark.asyncio
async def test_text_file_reader(component_controller, local_file_datasource):
    wid = str(uuid4())
    component = ComponentModel(
        workflow_id=wid,
        name="Text File Reader",
        class_name="TextFileReader",
        description="Text File Reader",
        group="IO",
        inputs=ComponentInput(
            key="input_file",
            data_type="File",
            value=local_file_datasource.to_component_input(
                component_controller.persistence_layer.get_user_file_root(
                    component_controller.config.DEFAULT_USER_PROFILE
                )
            ),
        ),
        output=ComponentOutput(data_type="TEXT", value=None),
    )

    result = await component_controller.run(component)
    result_value = (
        result.get(component.label, dict()).get("output", dict()).get("value")
    )
    assert result_value is not None and result_value == "LUNAR"
