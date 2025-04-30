from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
)
import logging

logging.basicConfig(level=logging.INFO)


@pytest.mark.asyncio
async def test_python_coder(component_controller, config):
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
                value="""result = 'abracadabra'""",
            ),
            output=ComponentOutput(data_type="ANY", value=None),
        )
    result = await component_controller.run(component, user_id=config.DEFAULT_USER_TEST_PROFILE)

    result_value = result.get('null', dict()).get("output", dict()).get("value")
    assert result_value is not None and result_value == "abracadabra"
