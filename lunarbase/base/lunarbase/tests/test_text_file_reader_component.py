from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
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
        inputs=[],
        output=ComponentOutput(data_type="TEXT", value=None),
        configuration={"datasource": local_file_datasource.id}
    )

    result = await component_controller.run(component)
    result_value = (
        result.get(component.label, dict()).get("output", dict()).get("value")
    )
    assert result_value is not None and result_value == "LUNAR"
