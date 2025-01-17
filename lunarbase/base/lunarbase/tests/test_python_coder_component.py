from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
)


@pytest.mark.asyncio
async def test_python_coder(component_controller):
    wid = str(uuid4())
    component = ComponentModel(
            workflow_id=wid,
            name="PythonCoder",
            class_name="PythonCoder",
            description="PythonCoder",
            group="CODERS",
            inputs=ComponentInput(
                key="code",
                data_type="Code",
                value="""from sortedcontainers import SortedSet
ss = SortedSet("{value}")
ss = "".join(ss)
result = ss""",
                template_variables={"code.value": "abracadabra"},
            ),
            output=ComponentOutput(data_type="ANY", value=None),
        )

    result = await component_controller.run(component)
    result_value = result.get(component.label, dict()).get("output", dict()).get("value")
    assert result_value is not None and result_value == "abcdr"
